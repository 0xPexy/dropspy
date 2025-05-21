import os
from pathlib import Path
from datetime import datetime
import google.generativeai as genai

TOKEN_COUNTING_MODEL_INSTANCE = None

def configure_tokenizer_model(api_key: str, model_name_for_counting: str):
    global TOKEN_COUNTING_MODEL_INSTANCE
    if api_key:
        genai.configure(api_key=api_key)
    try:
        TOKEN_COUNTING_MODEL_INSTANCE = genai.GenerativeModel(model_name_for_counting)
        print(f"Tokenizer model '{model_name_for_counting}' configured successfully for token counting.")
    except Exception as e:
        print(f"Error initializing GenerativeModel for token counting ('{model_name_for_counting}'): {e}")
        TOKEN_COUNTING_MODEL_INSTANCE = None

def count_tokens_official(text_content: str) -> int:
    if TOKEN_COUNTING_MODEL_INSTANCE is None:
        print("Warning: Official tokenizer not configured. Using rough heuristic (UTF-8 bytes / 2).")
        return len(text_content.encode("utf-8")) // 2
    if not text_content:
        return 0
    try:
        response = TOKEN_COUNTING_MODEL_INSTANCE.count_tokens(text_content)
        return response.total_tokens
    except Exception as e:
        print(f"Error counting tokens with official tokenizer: {e}. Using fallback heuristic.")
        return len(text_content.encode("utf-8")) // 2

def get_formatted_message_string(msg_data: dict) -> str:
    return (
        f"## 📡 Channel: {msg_data['channel']}\n"
        f"### 🕒 {msg_data['time']}\n"
        f"```text\n{msg_data['text']}\n```\n\n"
    )

def get_batch_timestamp_str(messages_in_batch: list) -> str:
    if not messages_in_batch:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        latest_datetime = max(datetime.strptime(m["time"], "%Y-%m-%d %H:%M") for m in messages_in_batch)
        return latest_datetime.strftime("%Y%m%d_%H%M")
    except (ValueError, TypeError):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

def split_messages_into_batches(
    all_messages: list,
    base_prompt_actual_tokens: int,
    max_tokens_for_single_api_call: int
) -> list:
    batches = []
    current_batch_message_objects = []
    current_tokens_for_formatted_messages_in_batch = 0
    tokens_available_for_formatted_messages = max_tokens_for_single_api_call - base_prompt_actual_tokens

    if tokens_available_for_formatted_messages <= 0:
        raise ValueError(
            f"Base prompt tokens ({base_prompt_actual_tokens}) are greater than or equal to "
            f"the max tokens allowed for a single API call ({max_tokens_for_single_api_call})."
        )

    for msg_data in all_messages:
        formatted_msg_str = get_formatted_message_string(msg_data)
        tokens_for_current_formatted_msg = count_tokens_official(formatted_msg_str)

        if tokens_for_current_formatted_msg > tokens_available_for_formatted_messages:
            print(f"Warning: Single formatted message from channel '{msg_data['channel']}' at {msg_data['time']} "
                  f"(est. {tokens_for_current_formatted_msg} tokens) "
                  f"is too large to fit. Skipping this message.")
            continue

        if (current_tokens_for_formatted_messages_in_batch + tokens_for_current_formatted_msg) > tokens_available_for_formatted_messages:
            if current_batch_message_objects:
                batches.append(current_batch_message_objects)
            current_batch_message_objects = [msg_data]
            current_tokens_for_formatted_messages_in_batch = tokens_for_current_formatted_msg
        else:
            current_batch_message_objects.append(msg_data)
            current_tokens_for_formatted_messages_in_batch += tokens_for_current_formatted_msg

    if current_batch_message_objects:
        batches.append(current_batch_message_objects)
    return batches

def write_message_batches_to_files(
    all_collected_messages: list,
    base_prompt_actual_tokens: int,
    lightweight_model_context_window_size: int,
    batch_target_window_percentage: float,
    output_dir_full_path: str,
    filename_prefix_timestamp: str = ""
) -> list:
    if TOKEN_COUNTING_MODEL_INSTANCE is None:
        print("CRITICAL ERROR: Tokenizer model (TOKEN_COUNTING_MODEL_INSTANCE) is not configured in batch_writer.")
        print("Call digest.batch_writer.configure_tokenizer_model() from your main script first.")
        return []

    os.makedirs(output_dir_full_path, exist_ok=True)
    target_max_tokens_for_api_call = int(lightweight_model_context_window_size * batch_target_window_percentage)

    sorted_messages = sorted(all_collected_messages, key=lambda x: x["time"])

    message_batches = split_messages_into_batches(
        sorted_messages,
        base_prompt_actual_tokens,
        target_max_tokens_for_api_call
    )

    written_file_names = []
    for i, single_batch_of_raw_messages in enumerate(message_batches):
        if not single_batch_of_raw_messages:
            continue
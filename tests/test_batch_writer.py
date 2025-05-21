# tests/test_batch_writer.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime

# Make sure the digest package can be imported.
# If your project structure is different, you might need to adjust the Python path
# or how you import (e.g., using relative imports if tests are inside the package).
# For this example, assuming 'your_project_root' is in PYTHONPATH or tests are run from there.
from digest.batch_writer import (
    split_messages_into_batches,
    write_message_batches_to_files,
    get_formatted_message_string, # Helper for consistent formatting in tests
    # TOKEN_COUNTING_MODEL_INSTANCE, # Global, avoid direct test manipulation if possible
    # configure_tokenizer_model # We will mock count_tokens_official directly
)

# --- Test Fixtures ---

@pytest.fixture
def sample_messages():
    """Provides a list of sample message dictionaries for testing."""
    return [
        {"channel": "channel_A", "time": "2025-05-20 10:00", "text": "Short message one."},
        {"channel": "channel_B", "time": "2025-05-20 10:05", "text": "This is a slightly longer message two."},
        {"channel": "channel_A", "time": "2025-05-20 10:10", "text": "A very long message three that will likely take up many tokens and push other messages to a new batch."},
        {"channel": "channel_C", "time": "2025-05-20 10:15", "text": "Message four."},
        {"channel": "channel_B", "time": "2025-05-20 10:20", "text": "Message five, also short."},
    ]

@pytest.fixture
def mock_count_tokens(mocker):
    """
    Mocks count_tokens_official to return a deterministic token count
    based on the length of the formatted string.
    This mock assumes 1 char = 1 token for simplicity in testing logic.
    Adjust if your actual tokenization is very different and you need to test that.
    """
    # The string passed to count_tokens_official in the new logic is the *formatted* message string.
    def simple_token_estimator(text_content: str) -> int:
        return len(text_content) # Simplistic: 1 char = 1 token for testing

    return mocker.patch("digest.batch_writer.count_tokens_official", side_effect=simple_token_estimator)


# --- Tests for split_messages_into_batches ---

def test_split_empty_messages_list(mock_count_tokens):
    """Test splitting with an empty list of messages."""
    batches = split_messages_into_batches(
        all_messages=[],
        base_prompt_actual_tokens=100,
        max_tokens_for_single_api_call=1000
    )
    assert batches == []

def test_split_all_messages_fit_one_batch(sample_messages, mock_count_tokens):
    """Test when all messages fit into a single batch."""
    # Token counts will be based on formatted strings.
    # Example: get_formatted_message_string(sample_messages[0])
    # Let's make max_tokens_for_single_api_call large enough.
    base_prompt_tokens = 50
    # Calculate total tokens for all formatted sample messages
    total_formatted_message_tokens = sum(len(get_formatted_message_string(m)) for m in sample_messages)
    
    max_api_call_tokens = base_prompt_tokens + total_formatted_message_tokens + 100 # Ensure enough space

    batches = split_messages_into_batches(
        all_messages=sample_messages,
        base_prompt_actual_tokens=base_prompt_tokens,
        max_tokens_for_single_api_call=max_api_call_tokens
    )
    assert len(batches) == 1
    assert len(batches[0]) == len(sample_messages)
    assert batches[0] == sample_messages # Order should be preserved if input is sorted

def test_split_messages_into_multiple_batches(sample_messages, mock_count_tokens):
    """Test splitting messages into multiple batches due to token limits."""
    base_prompt_tokens = 50
    # Set a limit that forces a split.
    # Calculate tokens for the first two formatted messages
    tokens_msg1_formatted = len(get_formatted_message_string(sample_messages[0]))
    tokens_msg2_formatted = len(get_formatted_message_string(sample_messages[1]))
    
    # Max API call tokens allows prompt + first two messages, but not the third.
    max_api_call_tokens = base_prompt_tokens + tokens_msg1_formatted + tokens_msg2_formatted + (len(get_formatted_message_string(sample_messages[2])) // 2)


    batches = split_messages_into_batches(
        all_messages=sample_messages, # Assumes sample_messages is sorted by time if that's a precondition
        base_prompt_actual_tokens=base_prompt_tokens,
        max_tokens_for_single_api_call=max_api_call_tokens
    )
    assert len(batches) > 1 # Should split
    # More specific assertions can be added based on expected split points
    # For example, if we know it splits after the 2nd message:
    assert len(batches[0]) == 2 
    assert batches[0][0] == sample_messages[0]
    assert batches[0][1] == sample_messages[1]
    
    # Verify total messages are preserved
    assert sum(len(batch) for batch in batches) == len(sample_messages)

def test_split_single_message_too_large_for_message_slot(sample_messages, mock_count_tokens, capsys):
    """Test that a message too large for the (max_call_tokens - prompt_tokens) slot is skipped."""
    base_prompt_tokens = 50
    # Make the available space for messages smaller than the smallest formatted message
    smallest_formatted_msg_tokens = min(len(get_formatted_message_string(m)) for m in sample_messages)
    max_api_call_tokens = base_prompt_tokens + smallest_formatted_msg_tokens -1 # Not enough space for any message

    batches = split_messages_into_batches(
        all_messages=sample_messages,
        base_prompt_actual_tokens=base_prompt_tokens,
        max_tokens_for_single_api_call=max_api_call_tokens
    )
    assert batches == [] # All messages should be skipped
    captured = capsys.readouterr()
    assert "Warning: Single formatted message" in captured.out # Check for warning print
    assert f"is too large to fit within the available message token limit of {max_api_call_tokens - base_prompt_tokens}" in captured.out


def test_split_prompt_too_large_raises_error(sample_messages, mock_count_tokens):
    """Test that an error is raised if the base prompt itself is too large."""
    base_prompt_tokens = 1000
    max_api_call_tokens = 900 # Prompt is larger than the total allowed

    with pytest.raises(ValueError, match="Base prompt tokens .* are greater than or equal to .*"):
        split_messages_into_batches(
            all_messages=sample_messages,
            base_prompt_actual_tokens=base_prompt_tokens,
            max_tokens_for_single_api_call=max_api_call_tokens
        )

def test_split_exact_fit_multiple_batches(mock_count_tokens):
    """Test where messages exactly fill up the allowed token space for messages."""
    msg1_text = "This is message one." # Assume formatted len = 20
    msg2_text = "This is message two, also twenty." # Assume formatted len = 30
    msg3_text = "Msg three." # Assume formatted len = 10

    # Mock count_tokens_official to return specific values for specific formatted texts
    def specific_token_estimator(text_content: str) -> int:
        if "message one" in text_content: return 20
        if "message two" in text_content: return 30
        if "Msg three" in text_content: return 10
        return len(text_content) # Fallback

    mocker = mock_count_tokens.mocker # Get the mocker object from the fixture
    mocker.patch("digest.batch_writer.count_tokens_official", side_effect=specific_token_estimator)

    messages = [
        {"channel": "test", "time": "2023-01-01 10:00", "text": msg1_text},
        {"channel": "test", "time": "2023-01-01 10:01", "text": msg2_text},
        {"channel": "test", "time": "2023-01-01 10:02", "text": msg3_text},
    ]
    
    base_prompt_tokens = 50
    # Available for messages = 100 - 50 = 50.
    # msg1 (20) + msg2 (30) = 50. So first batch should contain msg1, msg2.
    # msg3 (10) should be in the second batch.
    max_api_call_tokens = 100 

    batches = split_messages_into_batches(messages, base_prompt_tokens, max_api_call_tokens)
    
    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert batches[0][0]["text"] == msg1_text
    assert batches[0][1]["text"] == msg2_text
    assert len(batches[1]) == 1
    assert batches[1][0]["text"] == msg3_text


# --- Tests for write_message_batches_to_files ---

@pytest.fixture
def mock_batch_splitting(mocker):
    """Mocks the split_messages_into_batches function."""
    return mocker.patch("digest.batch_writer.split_messages_into_batches")

def test_write_no_messages(mock_batch_splitting, mock_count_tokens, tmp_path):
    """Test writing when there are no messages collected."""
    # We need to mock TOKEN_COUNTING_MODEL_INSTANCE or ensure count_tokens_official is fully mocked
    # The mock_count_tokens fixture already patches count_tokens_official globally for the test
    # but configure_tokenizer_model is usually called. For unit test, direct patch is better.
    # Here, we are primarily testing the flow if split_messages_into_batches returns empty.
    
    # Ensure TOKEN_COUNTING_MODEL_INSTANCE is mocked or count_tokens_official is patched
    # The mock_count_tokens fixture does this.
    # For this test, let's ensure split_messages_into_batches returns no batches.
    mock_batch_splitting.return_value = []

    # Critical: Ensure the global TOKEN_COUNTING_MODEL_INSTANCE is set for the check in write_message_batches_to_files
    # This would typically be done by calling configure_tokenizer_model in a setup or conftest.
    # For this isolated test, we can patch it directly or mock its check.
    # Alternatively, patch the check `if TOKEN_COUNTING_MODEL_INSTANCE is None:`
    # However, the `mock_count_tokens` fixture makes the `count_tokens_official` not rely on the global.
    # The check `if TOKEN_COUNTING_MODEL_INSTANCE is None:` at the start of `write_message_batches_to_files`
    # still needs to pass. Let's assume it's configured.
    # A better way for tests is to pass the model instance or make count_tokens not rely on global.
    # For now, let's assume our mock_count_tokens means the global instance check isn't the main issue.
    # We can also temporarily set it for the test.
    
    mocker = mock_count_tokens.mocker
    mocker.patch("digest.batch_writer.TOKEN_COUNTING_MODEL_INSTANCE", MagicMock()) # Ensure it's not None


    written_files = write_message_batches_to_files(
        all_collected_messages=[],
        base_prompt_actual_tokens=100,
        lightweight_model_context_window_size=100000, # Example value
        batch_target_window_percentage=0.8,
        output_dir_full_path=str(tmp_path) # Use pytest's tmp_path for temporary file operations
    )
    assert written_files == []
    mock_batch_splitting.assert_called_once() # Verifies it was called
    # Check that no files were created in tmp_path (or only the directory itself)
    assert len(list(tmp_path.iterdir())) == 0


def test_write_multiple_batches_creates_files(sample_messages, mock_batch_splitting, mock_count_tokens, tmp_path):
    """Test that files are created for multiple batches."""
    # Let split_messages_into_batches return a predefined set of batches
    # (sample_messages is a list of dicts)
    batch1 = [sample_messages[0], sample_messages[1]]
    batch2 = [sample_messages[2]]
    batch3 = [sample_messages[3], sample_messages[4]]
    mock_batch_splitting.return_value = [batch1, batch2, batch3]

    mocker = mock_count_tokens.mocker
    mocker.patch("digest.batch_writer.TOKEN_COUNTING_MODEL_INSTANCE", MagicMock())


    written_files = write_message_batches_to_files(
        all_collected_messages=sample_messages, # This will be sorted inside
        base_prompt_actual_tokens=50,
        lightweight_model_context_window_size=1000000,
        batch_target_window_percentage=0.8,
        output_dir_full_path=str(tmp_path),
        filename_prefix_timestamp="20250520_183000"
    )
    
    assert len(written_files) == 3
    # Check if files with expected names are created
    expected_filenames = [
        f"digest_20250520_183000_part1.md",
        f"digest_20250520_183000_part2.md",
        f"digest_20250520_183000_part3.md",
    ]
    for fname in expected_filenames:
        assert fname in written_files
        assert (tmp_path / fname).exists()
        # Optionally, check some basic content of the first file
        if fname == expected_filenames[0]:
            content = (tmp_path / fname).read_text(encoding="utf-8")
            assert f"# Telegram Message Batch - 20250520_183000 Part 1" in content
            assert f"## 📡 Channel: {sample_messages[0]['channel']}" in content # Assuming sample_messages are sorted by time by the function
            assert f"```text\n{sample_messages[0]['text']}\n```" in content


def test_write_batch_file_content_structure(sample_messages, mock_count_tokens, tmp_path):
    """Test the structure and key metadata in a written batch file."""
    # Using only one batch for simplicity to check content
    one_batch = [sample_messages[0], sample_messages[1]]
    
    mocker = mock_count_tokens.mocker # Get the mocker
    mock_split = mocker.patch("digest.batch_writer.split_messages_into_batches")
    mock_split.return_value = [one_batch]
    
    # Mock the global TOKEN_COUNTING_MODEL_INSTANCE for the check in write_message_batches_to_files
    mocker.patch("digest.batch_writer.TOKEN_COUNTING_MODEL_INSTANCE", MagicMock())


    base_prompt_tokens = 60
    # Using the mock_count_tokens which returns len(formatted_string)
    # Formatted string for msg0 and msg1
    msg0_formatted = get_formatted_message_string(sample_messages[0])
    msg1_formatted = get_formatted_message_string(sample_messages[1])
    tokens_batch_messages = len(msg0_formatted) + len(msg1_formatted)
    
    total_api_tokens_expected = base_prompt_tokens + tokens_batch_messages
    target_max_api_tokens = 1000000 # Does not matter much as split is mocked

    written_files = write_message_batches_to_files(
        all_collected_messages=[sample_messages[0], sample_messages[1]], # Input for sorting
        base_prompt_actual_tokens=base_prompt_tokens,
        lightweight_model_context_window_size=target_max_api_tokens, # model total context
        batch_target_window_percentage=0.8, # effective target for API call
        output_dir_full_path=str(tmp_path),
        filename_prefix_timestamp="testrun"
    )
    assert len(written_files) == 1
    file_path = tmp_path / written_files[0]
    assert file_path.exists()

    content = file_path.read_text(encoding="utf-8")
    assert f"External Base Prompt Tokens: approx. {base_prompt_tokens} tokens" in content
    assert f"Formatted Messages in this Batch - Est. Tokens: approx. {tokens_batch_messages} tokens" in content
    assert f"Total Estimated Tokens for API Call (Prompt + This Batch): approx. {total_api_tokens_expected} tokens" in content
    assert f"## 📡 Channel: {sample_messages[0]['channel']}" in content
    assert f"```text\n{sample_messages[0]['text']}\n```" in content
    assert f"## 📡 Channel: {sample_messages[1]['channel']}" in content
    assert f"```text\n{sample_messages[1]['text']}\n```" in content
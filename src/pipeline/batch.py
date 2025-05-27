import os
from typing import Any, Dict, List
from llm.tokenizer import Tokenizer

class BatchWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def make_batch_filename(
        self, messages: List[Dict], batch_idx: int, total_batches: int
    ) -> str:
        if not messages:
            return f"empty-batch_{batch_idx+1}of{total_batches}.md"
        t_format = "%Y%m%d_%H%M"
        try:
            start = messages[0]["time"]
            end = messages[-1]["time"]
        except (KeyError, IndexError):
            start = end = "unknown"
        return f"{start.replace(':','')}-{end.replace(':','')}-batch_{batch_idx+1}of{total_batches}.md"

    def write_batches(self, batches: List[List[Dict]]) -> List[str]:
        file_paths = []
        total = len(batches)
        for idx, batch in enumerate(batches):
            fname = self.make_batch_filename(batch, idx, total)
            fpath = os.path.join(self.output_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                for msg in batch:
                    f.write(f"## Channel: {msg.get('channel')}\n")
                    f.write(f"### Time: {msg.get('time')}\n")
                    f.write(f"```\n{msg.get('text')}\n```\n\n")
            file_paths.append(fname)
        return file_paths


class BatchSplitter:
    def __init__(
        self, tokenizer: Tokenizer, max_tokens_per_batch: int, base_prompt_tokens: int
    ):
        self.tokenizer = tokenizer
        self.max_tokens_per_batch = max_tokens_per_batch
        self.base_prompt_tokens = base_prompt_tokens

    def split(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        batches = []
        current_batch = []
        current_tokens = 0
        token_limit = self.max_tokens_per_batch - self.base_prompt_tokens

        for msg in messages:
            formatted = self.format_message(msg)
            msg_tokens = self.tokenizer.count_tokens(formatted)

            if msg_tokens > token_limit:
                print(
                    f"Message too long: {msg_tokens} tokens, max is {token_limit}, skipping..."
                )
                # Skip messages that are too big
                continue

            if current_tokens + msg_tokens > token_limit:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [msg]
                current_tokens = msg_tokens
            else:
                current_batch.append(msg)
                current_tokens += msg_tokens

        if current_batch:
            batches.append(current_batch)
        return batches

    def format_message(self, msg: Dict[str, Any]) -> str:
        # This is where you can inject your markdown or prompt formatting
        # Example markdown style:
        return (
            f"## Channel: {msg['channel']}\n"
            f"### {msg['time']}\n"
            f"```text\n{msg['text']}\n```\n"
        )


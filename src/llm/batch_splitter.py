from typing import List, Dict, Any
from llm.tokenizer import Tokenizer

class BatchSplitter:
    def __init__(self, tokenizer: Tokenizer, max_tokens_per_batch: int, base_prompt_tokens: int):
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

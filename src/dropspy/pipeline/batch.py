__all__ = ["BatchPipeline", "BatchStore"]

from pathlib import Path
from typing import Any, Dict, List
from dropspy.llm.tokenizer import Tokenizer
from dropspy.utils.formatting import jsonToStr
from dropspy.utils.json_store import JSONStore

class BatchPipeline:
    def __init__(
        self,
        output_dir: str,
        tokenizer: Tokenizer,
    ):
        self.store = BatchStore(data_dir=output_dir)
        self.splitter = _BatchSplitter(tokenizer=tokenizer)

    def run(
        self,
        max_tokens_per_batch: int,
        input_filename: str,
        prebatched_messages: List[Dict],
    ) -> List[str]:
        try:
            # Step 1: split messages into batches
            batches = self.splitter.split(
                max_tokens_per_batch,
                prebatched_messages,
            )
            # Step 2: store batches
            batch_file_paths = self.store.save(
                batches=batches, input_filename=input_filename
            )
            return batch_file_paths
        except Exception as e:
            raise RuntimeError(f"Error in batch pipeline: {e}")

    def _make_batch_filename(
        self,
        batch: List[Dict],
        batch_idx: int,
        total_batches: int,
        original_filename: str,
    ) -> str:
        if not batch:
            return f"empty-batch_{batch_idx+1}of{total_batches}.json"
        stem = Path(original_filename).stem
        return f"{stem}_batch_{batch_idx+1}of{total_batches}.json"


class BatchStore(JSONStore):
    def __init__(self, data_dir: str):
        super().__init__(data_dir)

    def save(
        self,
        batches: List[List[Dict]],
        input_filename: str,
    ) -> List[str]:
        try:
            saved_files = []
            stem = Path(input_filename).stem
            batch_dir = Path(self.data_dir) / stem
            batch_dir.mkdir(parents=True, exist_ok=True)

            total_batches = len(batches)
            for idx, messages in enumerate(batches):
                filename = f"{idx+1}of{total_batches}.json"
                path = batch_dir / filename
                message_dict = {str(i): message for i, message in enumerate(messages)}
                self._save(str(path), message_dict)
                saved_files.append(str(path))
            return saved_files
        except Exception as e:
            raise RuntimeError(f"Failed to store batches: {e}")


class _BatchSplitter:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def split(
        self,
        max_tokens_per_batch: int,
        messages: List[Dict[str, Any]],
    ) -> List[List[Dict[str, Any]]]:
        batches = []
        current_batch = []
        current_tokens = 0

        for msg in messages:
            formatted = jsonToStr(msg)
            msg_tokens = self.tokenizer.count_tokens(formatted)

            if msg_tokens > max_tokens_per_batch:
                # Skip messages that are too big
                print(
                    f"Message too big. Tokens: {msg_tokens} / Max: {max_tokens_per_batch}"
                )
                continue

            if current_tokens + msg_tokens > max_tokens_per_batch:
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

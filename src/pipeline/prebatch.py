import json
import os
from collections import Counter
from pathlib import Path
from typing import List, Dict
from utils.json_store import JSONStore


class PrebatchStore(JSONStore):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)

    def save(self, input_filename: str, prebatched_messages: List[Dict]) -> str:
        try:
            return self._save(Path(input_filename).name, prebatched_messages)
        except Exception as e:
            raise RuntimeError(f"Failed to store prebatced messages: {e}")


class Prebatcher:
    def __init__(self):
        pass

    def prebatch(self, fetched_messages: Dict) -> List[Dict]:
        try:
            text_counts = Counter(msg["text"] for msg in fetched_messages)
            seen = set()
            unique_messages = []
            for msg in fetched_messages:
                if msg["text"] not in seen:
                    msg_out = msg.copy()
                    msg_out["dup_count"] = text_counts[msg["text"]]
                    unique_messages.append(msg_out)
                    seen.add(msg["text"])
            return unique_messages
        except Exception as e:
            raise RuntimeError(f"An error occurred during prebatching: {e}")


class PrebatchPipeline:
    def __init__(self, output_dir: str):
        self.prebatchStore = PrebatchStore(output_dir=output_dir)
        self.prebatcher = Prebatcher()

    def run(self, input_filename: str, fetched_messages: Dict) -> str:
        try:
            unique_messages = self.prebatcher.prebatch(
                fetched_messages=fetched_messages
            )
            out_path = self.prebatchStore.save(input_filename, unique_messages)
            return out_path
        except Exception as e:
            raise RuntimeError(f"Error in prebatch pipeline: {e}")

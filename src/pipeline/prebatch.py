import json
import os
from collections import Counter
from pathlib import Path
from typing import List, Dict
from utils.json_file_store import JSONFileStore


class PrebatchStore(JSONFileStore):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)

    def store(self, input_file: str, messages: List[Dict]) -> str:
        try:
            return self.save(Path(input_file).name, messages)
        except Exception as e:
            raise RuntimeError(f"Failed to store messages: {e}")


class Prebatcher:
    def __init__(self):
        pass

    def prebatch(self, input_file: str) -> List[Dict]:
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                messages = json.load(f)

            text_counts = Counter(msg["text"] for msg in messages)
            seen = set()
            unique_messages = []
            for msg in messages:
                if msg["text"] not in seen:
                    msg_out = msg.copy()
                    msg_out["dup_count"] = text_counts[msg["text"]]
                    unique_messages.append(msg_out)
                    seen.add(msg["text"])
            return unique_messages
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {input_file}")
        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to decode JSON from file: {input_file}")
        except Exception as e:
            raise RuntimeError(f"An error occurred during prebatching: {e}")


class PrebatchPipeline:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.prebatcher = Prebatcher()

    def run(self, input_file: str) -> str:
        try:
            unique_messages = self.prebatcher.prebatch(input_file)
            store = PrebatchStore(self.output_dir)
            out_path = store.store(input_file, unique_messages)
            return out_path
        except Exception as e:
            raise RuntimeError(f"Error in prebatch pipeline: {e}")

# src/telegram/message_store.py

import os
import json
from typing import List, Dict
from datetime import datetime

class MessageStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def list_files(self):
        files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]
        files.sort()
        return files

    def print_file_list(self):
        files = self.list_files()
        for idx, fname in enumerate(files):
            print(f"{idx}: {fname}")

    def get_file_by_index(self, idx):
        files = self.list_files()
        if idx < 0 or idx >= len(files):
            raise IndexError("Invalid file index")
        return files[idx]
    
    def save_messages(self, messages: List[Dict]) -> str:
        if not messages:
            raise ValueError("No messages to save.")
        start = messages[0]["time"].replace(":", "").replace(" ", "_")
        end = messages[-1]["time"].replace(":", "").replace(" ", "_")
        filename = f"{start}~{end}.json"
        path = os.path.join(self.data_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return path

    def load_messages(self, filename: str) -> List[Dict]:
        path = os.path.join(self.data_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

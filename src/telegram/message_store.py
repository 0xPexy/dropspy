import os
import json
from typing import List, Dict
from utils.json_file_store import JSONFileStore


class MessageStore(JSONFileStore):
    def save_messages(self, messages: List[Dict]) -> str:
        if not messages:
            raise ValueError("No messages to save.")
        start = messages[0]["time"].replace(":", "").replace(" ", "_")
        end = messages[-1]["time"].replace(":", "").replace(" ", "_")
        filename = f"{start}~{end}.json"
        return self.save(filename, messages)

    def load_messages(self, filename: str) -> List[Dict]:
        return self.load(filename)

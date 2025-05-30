import os
import json
from typing import Dict, Mapping, Any


class JSONStore:
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

    def get_file_by_index(self, idx: int) -> Dict[str, Any]:
        files = self.list_files()
        if idx < 0 or idx >= len(files):
            raise IndexError("Invalid file index")
        filename = files[idx]
        content = self._load(filename)
        return {"filename": filename, "content": content}

    def _save(self, filename: str, data: Mapping[str, Any]) -> str:
        path = os.path.join(self.data_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save file: {path}") from e
        return path

    def _load(self, filename: str) -> dict:
        path = os.path.join(self.data_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")

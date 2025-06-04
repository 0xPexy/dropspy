from dataclasses import asdict, is_dataclass
import dataclasses
import logging
import os
import json
from typing import Dict, List, Mapping, Any, Sequence

logger = logging.getLogger(__name__)


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

    def _save(self, filename: str, data: Any) -> str:
        path = os.path.join(self.data_dir, filename)
        try:
            serializable_data = self._make_serializable(data)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save file: {path} - {e}")
            raise RuntimeError(e)
        return path

    def _load(self, filename: str) -> Any:
        path = os.path.join(self.data_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load file: {path} - {e}")
            return None

    def _make_serializable(self, obj: Any) -> Any:
        if hasattr(obj, "to_json") and callable(obj.to_json):
            return obj.to_json()

        if is_dataclass(obj) and not isinstance(obj, type):
            return {k: self._make_serializable(v) for k, v in asdict(obj).items()}

        if isinstance(obj, Mapping):
            return {str(k): self._make_serializable(v) for k, v in obj.items()}

        if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
            return [self._make_serializable(item) for item in obj]

        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj

        return str(obj)

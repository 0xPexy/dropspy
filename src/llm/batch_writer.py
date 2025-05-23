# src/llm/batch_writer.py

import os
from typing import List, Dict

class FileBatchWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def make_batch_filename(self, messages: List[Dict], batch_idx: int, total_batches: int) -> str:
        if not messages:
            return f"empty-batch_{batch_idx+1}of{total_batches}.md"
        t_format = "%Y%m%d_%H%M"
        try:
            start = messages[0]['time']
            end = messages[-1]['time']
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

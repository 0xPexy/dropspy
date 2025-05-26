import json
import os
from collections import Counter, defaultdict
from pathlib import Path


def prebatch(input_file: str, output_dir: str):
    # Load messages
    with open(input_file, "r", encoding="utf-8") as f:
        messages = json.load(f)

    # Count duplicates
    text_counts = Counter(msg["text"] for msg in messages)

    # Unique messages with dup_count
    unique_messages = []
    seen = set()
    for msg in messages:
        if msg["text"] not in seen:
            msg_out = msg.copy()
            msg_out["dup_count"] = text_counts[msg["text"]]
            unique_messages.append(msg_out)
            seen.add(msg["text"])
    # Output file name
    out_path = Path(output_dir) / Path(input_file).name
    os.makedirs(out_path.parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique_messages, f, ensure_ascii=False, indent=2)
    return out_path

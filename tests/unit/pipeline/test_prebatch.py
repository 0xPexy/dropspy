import json
from pipeline.prebatch import prebatch

def test_prebatch(tmp_path):
    messages = [
        {"channel": "a", "time": "1", "text": "hello world"},
        {"channel": "b", "time": "2", "text": "hello world"},
        {"channel": "c", "time": "3", "text": "unique message"},
    ]
    input_file = tmp_path / "test_messages.json"
    output_dir = tmp_path

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(messages, f)

    out_file = prebatch(str(input_file), str(output_dir))

    with open(out_file, "r", encoding="utf-8") as f:
        result = json.load(f)

    assert len(result) == 2
    texts = {msg["text"]: msg for msg in result}
    assert texts["hello world"]["dup_count"] == 2
    assert texts["unique message"]["dup_count"] == 1

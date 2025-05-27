import pytest
import json
from pathlib import Path
from pipeline.prebatch import PrebatchPipeline

@pytest.fixture
def test_messages():
    return [
        {"channel": "a", "time": "1", "text": "same"},
        {"channel": "b", "time": "2", "text": "same"},
        {"channel": "c", "time": "3", "text": "unique"}
    ]

def test_prebatch_pipeline_dedup(tmp_path, test_messages):
    # 정상 케이스: 중복 메시지 존재
    input_file = tmp_path / "input.json"
    output_dir = tmp_path / "out"
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(test_messages, f)
    pipeline = PrebatchPipeline(str(output_dir))
    out_path = pipeline.run(str(input_file))

    with open(out_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert len(result) == 2
    texts = {msg["text"]: msg for msg in result}
    assert texts["same"]["dup_count"] == 2
    assert texts["unique"]["dup_count"] == 1

def test_prebatch_pipeline_no_duplicates(tmp_path):
    # 중복 없는 경우
    messages = [
        {"channel": "a", "time": "1", "text": "x"},
        {"channel": "b", "time": "2", "text": "y"}
    ]
    input_file = tmp_path / "input.json"
    output_dir = tmp_path / "out"
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(messages, f)
    pipeline = PrebatchPipeline(str(output_dir))
    out_path = pipeline.run(str(input_file))
    with open(out_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert len(result) == 2
    for msg in result:
        assert msg["dup_count"] == 1

def test_prebatch_pipeline_file_not_found(tmp_path):
    pipeline = PrebatchPipeline(str(tmp_path))
    with pytest.raises(RuntimeError) as e:
        pipeline.run(str(tmp_path / "notfound.json"))
    assert "File not found" in str(e.value)

def test_prebatch_pipeline_json_decode_error(tmp_path):
    # 에러 케이스: 잘못된 JSON
    bad_file = tmp_path / "bad.json"
    output_dir = tmp_path / "out"
    with open(bad_file, "w", encoding="utf-8") as f:
        f.write("not a json")
    pipeline = PrebatchPipeline(str(output_dir))
    with pytest.raises(RuntimeError) as e:
        pipeline.run(str(bad_file))
    assert "Failed to decode JSON" in str(e.value)

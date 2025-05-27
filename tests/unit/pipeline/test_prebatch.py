import pytest
import json
from pathlib import Path
from pipeline.prebatch import PrebatchPipeline


@pytest.fixture
def test_messages():
    return [
        {"channel": "a", "time": "1", "text": "same"},
        {"channel": "b", "time": "2", "text": "same"},
        {"channel": "c", "time": "3", "text": "unique"},
    ]


def test_prebatch_pipeline_dedup(tmp_path, test_messages):
    input_filename = tmp_path / "input.json"
    output_dir = tmp_path / "out"
    pipeline = PrebatchPipeline(str(output_dir))
    out_path = pipeline.run(str(input_filename), test_messages)

    with open(out_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert len(result) == 2
    texts = {msg["text"]: msg for msg in result}
    assert texts["same"]["dup_count"] == 2
    assert texts["unique"]["dup_count"] == 1


def test_prebatch_pipeline_no_duplicates(tmp_path):
    messages = [
        {"channel": "a", "time": "1", "text": "x"},
        {"channel": "b", "time": "2", "text": "y"},
    ]
    input_filename = tmp_path / "input.json"
    output_dir = tmp_path / "out"
    pipeline = PrebatchPipeline(str(output_dir))
    out_path = pipeline.run(str(input_filename), messages)
    with open(out_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    assert len(result) == 2
    for msg in result:
        assert msg["dup_count"] == 1

from pathlib import Path
from llm.tokenizer import Tokenizer
import pytest
from pipeline.batch import _BatchSplitter, BatchPipeline
from pipeline.batch import _BatchStore
from datetime import datetime, timedelta

from utils.formatting import jsonToStr


class DummyTokenizer(Tokenizer):
    def count_tokens(self, text):
        return len(text) // 4


@pytest.mark.parametrize(
    "max_tokens",
    [40, 90, 25],
)
def test_batch_split_cases(max_tokens):
    messages = [
        {"channel": "A", "time": "2025-01-01 12:00", "text": "hello", "dup_count": 1},
        {"channel": "A", "time": "2025-01-01 12:01", "text": "world"},
        {
            "channel": "A",
            "time": "2025-01-01 12:02",
            "text": "hi there, this is a long message for token testing.",
            "dup_count": 3,
        },
        {
            "channel": "B",
            "time": "2025-01-01 12:03",
            "text": "에어드랍 참여법을 알려주세요.",
            "dup_count": 42,
        },
        {"channel": "B", "time": "2025-01-01 12:04", "text": "멀티라인\n메시지\ntest!"},
        {
            "channel": "B",
            "time": "2025-01-01 12:05",
            "text": "# Markdown Title\n- Item1\n- Item2\nEnd.",
            "dup_count": 18,
        },
        {"channel": "C", "time": "2025-01-01 12:06", "text": "Short", "dup_count": 1},
        {"channel": "C", "time": "2025-01-01 12:07", "text": "x" * 80, "dup_count": 1},
        {
            "channel": "C",
            "time": "2025-01-01 12:08",
            "text": "한글" * 10,
            "dup_count": 0,
        },
        {
            "channel": "C",
            "time": "2025-01-01 12:09",
            "text": "Final quick test.",
            "dup_count": 1,
        },
    ]
    tokenizer = DummyTokenizer()
    batcher = _BatchSplitter(tokenizer=tokenizer)
    batches = batcher.split(max_tokens_per_batch=max_tokens, messages=messages)
    for batch in batches:
        total_tokens = sum(tokenizer.count_tokens(jsonToStr(m)) for m in batch)
        assert total_tokens <= max_tokens


def sample_batches():
    return [
        {
            "messages": [
                {
                    "channel": "A",
                    "time": "20240524_1000",
                    "text": "Hello",
                    "dup_count": 1,
                },
                {
                    "channel": "A",
                    "time": "20240524_1010",
                    "text": "World",
                    "dup_count": 1,
                },
            ],
        },
        {
            "messages": [
                {
                    "channel": "B",
                    "time": "20240524_1030",
                    "text": "에어드랍 참여법",
                    "dup_count": 1,
                },
            ],
        },
    ]


def test_store_stores_files(tmp_path):
    store = _BatchStore(data_dir=str(tmp_path))
    batches_with_filenames = sample_batches()
    batches = [b["messages"] for b in batches_with_filenames]
    input_filename = "input"
    files = store.store(batches, f"{input_filename}.json")
    assert len(files) == len(batches)
    for fname, batch in zip(files, batches):
        fpath = tmp_path / fname
        assert fpath.exists()
        content = fpath.read_text(encoding="utf-8")
        for msg in batch:
            assert msg["channel"] in content
            assert msg["time"] in content
            assert msg["text"] in content
            assert str(msg["dup_count"]) in content


@pytest.fixture
def batch_pipeline(tmp_path):
    tokenizer = DummyTokenizer()
    pipeline = BatchPipeline(output_dir=str(tmp_path), tokenizer=tokenizer)
    return pipeline


def test_run_creates_files(batch_pipeline, tmp_path):
    prebatched_messages = [
        {"channel": "@chan1", "time": "2023-01-01 10:00", "text": "msg1"},  # 16 tokens
        {"channel": "@chan1", "time": "2023-01-01 10:01", "text": "msg2"},
        {"channel": "@chan1", "time": "2023-01-01 10:02", "text": "msg3"},
        {"channel": "@chan2", "time": "2023-01-01 10:03", "text": "msg4"},
        {"channel": "@chan2", "time": "2023-01-01 10:04", "text": "msg5"},
        {"channel": "@chan3", "time": "2023-01-01 10:05", "text": "msg6"},
    ]
    max_tokens = 32
    input_filename = "2025-05-19_1330~2025-05-26_1323"
    batch_files = batch_pipeline.run(
        max_tokens_per_batch=max_tokens,
        input_filename=f"{tmp_path}/{input_filename}.json",
        prebatched_messages=prebatched_messages,
    )

    for idx, f in enumerate(batch_files):
        fpath = Path(f)
        assert fpath.exists()
        assert fpath.parent.name == input_filename
        assert fpath.name == f"{idx+1}of{len(batch_files)}.json"
        content = fpath.read_text(encoding="utf-8")
        for msg in prebatched_messages:
            if msg["text"] in content:
                assert True
    assert len(batch_files) == 3

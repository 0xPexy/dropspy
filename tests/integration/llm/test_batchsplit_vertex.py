# tests/integration/test_batchsplit_vertex.py

import pytest
from pipeline.batch import BatchSplitter
from llm.tokenizer import VertexTokenizer


@pytest.mark.integration
def test_batchsplitter_with_vertex_tokenizer():
    tokenizer = VertexTokenizer("gemini-1.5-flash-001")
    splitter = BatchSplitter(tokenizer, max_tokens_per_batch=50, base_prompt_tokens=10)

    messages = [
        {"channel": "A", "time": "2025-01-01 12:00", "text": "hello"},
        {"channel": "A", "time": "2025-01-01 12:01", "text": "world"},
        {
            "channel": "A",
            "time": "2025-01-01 12:02",
            "text": "hi there, this is a long message for token testing.",
        },
        {
            "channel": "B",
            "time": "2025-01-01 12:03",
            "text": "에어드랍 참여법을 알려주세요.",
        },
        {"channel": "B", "time": "2025-01-01 12:04", "text": "멀티라인\n메시지\ntest!"},
        {
            "channel": "B",
            "time": "2025-01-01 12:05",
            "text": "# Markdown Title\n- Item1\n- Item2\nEnd.",
        },
        {"channel": "C", "time": "2025-01-01 12:06", "text": "Short"},
        {"channel": "C", "time": "2025-01-01 12:07", "text": "x" * 80},
        {"channel": "C", "time": "2025-01-01 12:08", "text": "한글" * 10},
        {"channel": "C", "time": "2025-01-01 12:09", "text": "Final quick test."},
    ]

    batches = splitter.split(messages)

    for i, batch in enumerate(batches):
        tokens = sum(tokenizer.count_tokens(splitter.format_message(m)) for m in batch)
        print(f"Batch {i+1}: {len(batch)} messages, {tokens} tokens")
        for m in batch:
            print(f"   - [{m['channel']}] {m['time']} : {m['text'][:40]}...")
        assert tokens <= (splitter.max_tokens_per_batch - splitter.base_prompt_tokens)

    all_texts = [m["text"] for b in batches for m in b]
    assert set(all_texts).issubset([msg["text"] for msg in messages])

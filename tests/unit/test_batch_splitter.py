import pytest
from llm.batch_splitter import BatchSplitter


class DummyTokenizer:
    def count_tokens(self, text):
        return len(text) // 4


@pytest.mark.parametrize(
    "max_tokens, base_prompt",
    [
        (50, 10),
        (100, 10),
        (30, 5),
    ],
)
def test_batch_split_cases(max_tokens, base_prompt):
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
    splitter = BatchSplitter(DummyTokenizer(), max_tokens, base_prompt)
    batches = splitter.split(messages)
    for batch in batches:
        total_tokens = sum(
            splitter.tokenizer.count_tokens(splitter.format_message(m)) for m in batch
        )
        assert total_tokens <= (max_tokens - base_prompt)
        print(f"Batch: {len(batch)} messages, {total_tokens} tokens")

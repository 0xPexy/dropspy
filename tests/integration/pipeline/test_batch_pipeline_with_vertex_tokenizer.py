import pytest
from llm.tokenizer import VertexTokenizer
from pipeline.batch import BatchPipeline
from datetime import datetime, timedelta


@pytest.mark.integration
def test_batch_pipeline_with_vertex_tokenizer(tmp_path):
    tokenizer = VertexTokenizer(model_name="gemini-1.5-flash-001")

    base_time = datetime(2025, 5, 10, 9, 0)
    messages = []
    for i in range(30):
        t = base_time + timedelta(minutes=30 * i)
        messages.append(
            {
                "channel": chr(65 + (i % 3)),
                "time": t.strftime("%Y%m%d_%H%M"),
                "text": f"통합테스트 메시지 {i+1}",
                "dup_count": 0,
            }
        )

    max_tokens_per_batch = 128
    batch_pipeline = BatchPipeline(
        output_dir=str(tmp_path),
        tokenizer=tokenizer,
    )
    input_filename = tmp_path / "test_input.json"
    batch_file_paths = batch_pipeline.run(
        max_tokens_per_batch=max_tokens_per_batch,
        input_filename=input_filename,
        prebatched_messages=messages,
    )

    expeted_batch_count = 15
    assert len(batch_file_paths) == expeted_batch_count

    for idx, fname in enumerate(batch_file_paths):
        fpath = tmp_path / fname
        assert fpath.exists()
        assert f"{idx+1}of{expeted_batch_count}" in fname

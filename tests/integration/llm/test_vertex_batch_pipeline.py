import pytest
from llm.tokenizer import VertexTokenizer
from llm.batch_splitter import BatchSplitter
from llm.batch_writer import FileBatchWriter
from datetime import datetime, timedelta

@pytest.mark.integration
def test_vertex_tokenizer_batch_pipeline(tmp_path):
    tokenizer = VertexTokenizer(model_name="gemini-1.5-flash-001")

    base_time = datetime(2025, 5, 10, 9, 0)
    messages = []
    for i in range(30):
        t = base_time + timedelta(minutes=30 * i)
        messages.append({
            "channel": chr(65 + (i % 3)),  
            "time": t.strftime("%Y%m%d_%H%M"),
            "text": f"통합테스트 메시지 {i+1}"
        })

    max_tokens_per_batch = 128 
    base_prompt_tokens = 10
    splitter = BatchSplitter(tokenizer, max_tokens_per_batch, base_prompt_tokens)
    batches = splitter.split(messages)
    assert len(batches) == 10

    writer = FileBatchWriter(output_dir=str(tmp_path))
    files = writer.write_batches(batches)
    assert len(files) == 10

    for idx, (fname, batch) in enumerate(zip(files, batches)):
        fpath = tmp_path / fname
        assert fpath.exists()
        
        assert batch[0]["time"].replace(":", "") in fname
        assert batch[-1]["time"].replace(":", "") in fname
        assert f"batch_{idx+1}of10" in fname
        
        content = fpath.read_text(encoding="utf-8")
        for msg in batch:
            assert msg["channel"] in content
            assert msg["time"] in content
            assert msg["text"] in content

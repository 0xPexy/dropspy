# tests/unit/test_batch_writer.py
from llm.batch_writer import FileBatchWriter
from datetime import datetime, timedelta


def sample_batches():
    return [
        [
            {"channel": "A", "time": "20240524_1000", "text": "Hello"},
            {"channel": "A", "time": "20240524_1010", "text": "World"},
        ],
        [
            {"channel": "B", "time": "20240524_1030", "text": "에어드랍 참여법"},
        ],
    ]


def test_filebatchwriter_creates_files(tmp_path):
    writer = FileBatchWriter(output_dir=str(tmp_path))
    batches = sample_batches()
    files = writer.write_batches(batches)
    assert len(files) == len(batches)
    for fname, batch in zip(files, batches):
        fpath = tmp_path / fname
        assert fpath.exists()
        content = fpath.read_text(encoding="utf-8")
        for msg in batch:
            assert msg["channel"] in content
            assert msg["time"] in content
            assert msg["text"] in content


def test_empty_batch_file(tmp_path):
    writer = FileBatchWriter(output_dir=str(tmp_path))
    batches = [[]]
    files = writer.write_batches(batches)
    assert len(files) == 1
    fpath = tmp_path / files[0]
    assert fpath.exists()
    assert "empty-batch_1of1" in files[0]


def complex_batches(num_batches=10, msgs_per_batch=3):
    base_time = datetime(2024, 5, 24, 10, 0)
    batches = []
    for i in range(num_batches):
        batch = []
        for j in range(msgs_per_batch):
            t = base_time + timedelta(minutes=(i * msgs_per_batch + j) * 10)
            msg = {
                "channel": chr(65 + (i % 3)),  
                "time": t.strftime("%Y%m%d_%H%M"),
                "text": f"메시지 {i*msgs_per_batch + j + 1} (배치 {i+1})",
            }
            batch.append(msg)
        batches.append(batch)
    return batches


def test_filebatchwriter_multiple_batches(tmp_path):
    writer = FileBatchWriter(output_dir=str(tmp_path))
    batches = complex_batches(num_batches=10, msgs_per_batch=3)
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

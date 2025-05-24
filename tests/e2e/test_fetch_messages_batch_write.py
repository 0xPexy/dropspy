import os
import tempfile
import json
from datetime import datetime, timedelta, timezone

from llm.batch_splitter import BatchSplitter
from llm.batch_writer import BatchWriter
from llm.tokenizer import VertexTokenizer
import pytest
from dotenv import load_dotenv

from telegram.message_fetcher import MessageFetcher
from telegram.chat_info_fetcher import ChatInfoFetcher

load_dotenv(dotenv_path=".env.test")
KST = timezone(timedelta(hours=9))


@pytest.fixture
def tmp_last_fetch_file():
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def tmp_batch_dir():
    d = tempfile.TemporaryDirectory()
    yield d.name
    d.cleanup()


def test_fetch_and_batch_real_api_file_absent(tmp_last_fetch_file, tmp_batch_dir):
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session = os.getenv("TELEGRAM_SESSION_NAME")
    chats = [x.strip() for x in os.getenv("TELEGRAM_TARGET_CHATS").split(",")]
    fetcher = MessageFetcher(
        api_id=api_id,
        api_hash=api_hash,
        session_name=session,
        target_chats=chats,
        last_fetch_path=tmp_last_fetch_file,
        default_fetch_days=1,
    )
    msgs = fetcher.fetch()
    assert isinstance(msgs, list)
    assert all("text" in m for m in msgs)
    assert os.path.exists(tmp_last_fetch_file)
    with open(tmp_last_fetch_file) as f:
        last = json.load(f)
    assert isinstance(last, dict)

    tokenizer = VertexTokenizer()
    max_tokens_per_batch = 300
    base_prompt_tokens = 50
    splitter = BatchSplitter(
        tokenizer,
        max_tokens_per_batch=max_tokens_per_batch,
        base_prompt_tokens=base_prompt_tokens,
    )

    batches = splitter.split(msgs)
    assert isinstance(batches, list)
    assert all(isinstance(batch, list) for batch in batches)
    filtered_msgs = [
        m
        for m in msgs
        if tokenizer.count_tokens(splitter.format_message(m))
        <= max_tokens_per_batch - base_prompt_tokens
    ]
    assert sum(len(batch) for batch in batches) == len(filtered_msgs)

    writer = BatchWriter(output_dir=tmp_batch_dir)
    file_names = writer.write_batches(batches)
    assert isinstance(file_names, list)
    assert len(file_names) == len(batches)

    for fname in file_names:
        fpath = os.path.join(tmp_batch_dir, fname)
        assert os.path.exists(fpath)
        with open(fpath) as f:
            content = f.read()
            assert isinstance(content, str)
            assert any(m["text"] in content for m in filtered_msgs)

    print(f"batch file count: {len(file_names)}, dir: {tmp_batch_dir}")


def test_fetch_and_batch_real_api_file_present(tmp_last_fetch_file, tmp_batch_dir):
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session = os.getenv("TELEGRAM_SESSION_NAME")
    chats = [x.strip() for x in os.getenv("TELEGRAM_TARGET_CHATS").split(",")]

    base_time = datetime.now(KST) - timedelta(days=2)
    fetch_record = {}

    chat_info_fetcher = ChatInfoFetcher(
        api_id=api_id, api_hash=api_hash, session_name=session
    )
    for chat in chats:
        chat_id = chat_info_fetcher.get_id_by_handle(chat)
        fetch_record[chat_id] = {
            "handle": chat,
            "last_fetch": base_time.strftime("%Y-%m-%d %H:%M"),
        }
    print("fetch_record", fetch_record)
    with open(tmp_last_fetch_file, "w") as f:
        json.dump(fetch_record, f, ensure_ascii=False, indent=2)

    fetcher = MessageFetcher(
        api_id=api_id,
        api_hash=api_hash,
        session_name=session,
        target_chats=chats,
        last_fetch_path=tmp_last_fetch_file,
        default_fetch_days=3,
    )
    msgs = fetcher.fetch()
    assert isinstance(msgs, list)
    assert all("text" in m for m in msgs)

    for m in msgs:
        t = datetime.strptime(m["time"], "%Y-%m-%d %H:%M").replace(tzinfo=KST)
        assert t > base_time

    tokenizer = VertexTokenizer()
    max_tokens_per_batch = 300
    base_prompt_tokens = 50
    splitter = BatchSplitter(
        tokenizer,
        max_tokens_per_batch=max_tokens_per_batch,
        base_prompt_tokens=base_prompt_tokens,
    )

    batches = splitter.split(msgs)
    assert isinstance(batches, list)
    assert all(isinstance(batch, list) for batch in batches)
    filtered_msgs = [
        m
        for m in msgs
        if tokenizer.count_tokens(splitter.format_message(m))
        <= max_tokens_per_batch - base_prompt_tokens
    ]
    assert sum(len(batch) for batch in batches) == len(filtered_msgs)

    writer = BatchWriter(output_dir=tmp_batch_dir)
    file_names = writer.write_batches(batches)
    assert isinstance(file_names, list)
    assert len(file_names) == len(batches)

    for fname in file_names:
        fpath = os.path.join(tmp_batch_dir, fname)
        assert os.path.exists(fpath)
        with open(fpath) as f:
            content = f.read()
            assert isinstance(content, str)
            assert any(m["text"] in content for m in filtered_msgs)

    print(f"batch file count: {len(file_names)}, dir: {tmp_batch_dir}")

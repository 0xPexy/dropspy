# tests/integration/test_message_fetcher_integration.py

import os
from dotenv import load_dotenv
from telegram.message_fetcher import MessageFetcher

def test_message_fetcher_integration(tmp_path):
    load_dotenv(dotenv_path=".env.test")
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_name = os.getenv("TELEGRAM_SESSION_NAME")
    target_chats = os.getenv("TELEGRAM_TARGET_CHATS").split(",")
    last_fetch_path = tmp_path / "fetch.json"
    default_days = int(os.getenv("TELEGRAM_DEFAULT_FETCH_DAYS", "7"))

    fetcher = MessageFetcher(api_id, api_hash, session_name, target_chats, str(last_fetch_path), default_days)
    msgs = fetcher.fetch()
    assert isinstance(msgs, list)
    for m in msgs:
        assert set(m.keys()) == {"channel", "time", "text"}
        print(m)

import pytest
from telegram.message_fetcher import MessageFetcher
from datetime import datetime, timedelta, timezone
from collections import Counter

KST = timezone(timedelta(hours=9))


class DummyClient:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_entity(self, chat):
        # Differentiate channel by chat name/id
        entity = type(
            "Entity",
            (),
            {"id": str(hash(chat)), "username": chat if chat.startswith("@") else None},
        )()
        return entity

    def __call__(self, req):
        now = datetime(2025, 5, 20, 12, 0, tzinfo=KST)
        msgs = []
        # 3 in-range messages
        for i in range(3):
            msg = type("Msg", (), {})()
            msg.date = now - timedelta(days=i)
            msg.message = f"{req.peer.username} message {i}"
            msgs.append(msg)
        # 1 duplicate (just append same message with same content/date)
        dup_msg = type("Msg", (), {})()
        dup_msg.date = now - timedelta(days=1)
        dup_msg.message = f"{req.peer.username} message 1"
        msgs.append(dup_msg)
        # 2 out-of-range messages
        for i in range(2):
            msg = type("Msg", (), {})()
            msg.date = now - timedelta(days=10 + i)
            msg.message = f"{req.peer.username} old message {i}"
            msgs.append(msg)
        return type("History", (), {"messages": msgs})()

    def is_connected(self):
        return True

    def is_user_authorized(self):
        return True


@pytest.fixture
def mock_fetcher(monkeypatch):
    monkeypatch.setattr("telegram.message_fetcher.TelegramClient", DummyClient)

    class TestableMessageFetcher(MessageFetcher):
        def _load_last_fetch_times(self):
            # Only the first channel has last_fetch (3 days ago), second is empty
            return {
                str(hash("@chan1")): {
                    "handle": "@chan1",
                    "last_fetch": datetime(2025, 5, 17, 0, 0, tzinfo=KST).isoformat(),
                }
            }

        def _save_last_fetch_times(self, last_fetch_times):
            self.saved_fetch_times = last_fetch_times

    return TestableMessageFetcher(
        api_id=111,
        api_hash="xxx",
        session_name="test",
        target_chats=["@chan1", "@chan2"],
        last_fetch_path="unused.json",
        default_fetch_days=7,
    )


def test_message_fetcher_logic(mock_fetcher):
    now = datetime(2025, 5, 20, 12, 0, tzinfo=KST)
    msgs = mock_fetcher.fetch(now=now)
    # Each channel should have 6 messages in range (3 in range, 1 duplicate, plus channel offset)
    assert len(msgs) == 8
    # Check chronological order
    times = [m["time"] for m in msgs]
    assert times == sorted(times)
    # Channel 1: messages from last_fetch (2025-05-17) to 2025-05-20
    ch1_msgs = [m for m in msgs if m["channel"] == "@chan1"]
    # Channel 2: messages from default_fetch_days (2025-05-13) to 2025-05-20
    ch2_msgs = [m for m in msgs if m["channel"] == "@chan2"]
    assert all(
        datetime.strptime(m["time"], "%Y-%m-%d %H:%M") >= datetime(2025, 5, 17, 0, 0)
        for m in ch1_msgs
    )
    assert all(
        datetime.strptime(m["time"], "%Y-%m-%d %H:%M") >= datetime(2025, 5, 13, 0, 0)
        for m in ch2_msgs
    )
    # Duplicates should exist
    counts = Counter(m["text"] for m in msgs)
    assert any(v > 1 for v in counts.values())

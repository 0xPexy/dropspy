from datetime import datetime, timedelta, timezone
import json
from typing import cast
import pytest

from dropspy.pipeline.fetch import FetchStore, run_fetch_pipeline
from dropspy.telegram.types import RawMessage


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_fetch_without_file_e2e(
    test_e2e_logger,
    api_adapter,
    target_chats,
    tmp_msg_dir,
):
    if len(target_chats) == 0:
        pytest.skip("Skipping fetch_channel_messages test: no target chats specified")
    MAX_TARGET_CHATS = 3
    if len(target_chats) > MAX_TARGET_CHATS:
        target_chats = target_chats[:MAX_TARGET_CHATS]
    try:
        await api_adapter.connect()
        fetch_store = FetchStore(tmp_msg_dir)
        days_interval = 3
        now = datetime.now(tz=timezone.utc)
        last_fetched = now - timedelta(days=days_interval)
        last_fetched_str = last_fetched.isoformat()
        message_file_path = await run_fetch_pipeline(
            fetch_store=fetch_store,
            telegram_api_adapter=api_adapter,
            channel_handles=target_chats,
            start=last_fetched,
            end=now,
        )

        messages = fetch_store.load_messages_by_filename(message_file_path)
        for message in messages:
            assert message.validate()
            assert message.channel_handle in target_chats
            assert message.time > last_fetched_str
    except Exception as e:
        test_e2e_logger.error(e)
        pytest.fail(str(e))
    finally:
        await api_adapter.disconnect()

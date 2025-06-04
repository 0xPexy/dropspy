from datetime import datetime, timedelta, timezone
from typing import List
import pytest
from dropspy.pipeline.fetch import FetchStore, run_fetch_pipeline
from dropspy.telegram.api_adapter import TelegramAPIAdapter


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
    test_e2e_logger.info("Running test_fetch_without_file_e2e")
    fetch_store = FetchStore(tmp_msg_dir)
    assert fetch_store.load_last_fetch_times() == None
    await run_and_validate(
        api_adapter=api_adapter,
        fetch_store=fetch_store,
        target_chats=target_chats,
        last_fetched=datetime.now(tz=timezone.utc) - timedelta(days=3),
        end=datetime.now(tz=timezone.utc),
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_fetch_with_file_e2e(
    test_e2e_logger,
    api_adapter,
    target_chats,
    tmp_msg_dir,
):
    if len(target_chats) == 0:
        pytest.skip("Skipping fetch_channel_messages test: no target chats specified")
    test_e2e_logger.info("Running test_fetch_with_file_e2e")
    days_interval = 3

    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(days=days_interval)
    fetch_store = FetchStore(tmp_msg_dir)
    fetch_store.save_last_fetch_times(start)

    for i in range(days_interval):
        loaded_last_fetch = fetch_store.load_last_fetch_times()
        assert loaded_last_fetch is not None
        assert loaded_last_fetch == start + timedelta(days=i)
        await run_and_validate(
            api_adapter=api_adapter,
            fetch_store=fetch_store,
            target_chats=target_chats,
            last_fetched=loaded_last_fetch,
            end=start + timedelta(days=i + 1),
        )


async def run_and_validate(
    api_adapter: TelegramAPIAdapter,
    fetch_store: FetchStore,
    target_chats: List[str],
    last_fetched: datetime,
    end: datetime,
):
    message_file_path = await run_fetch_pipeline(
        fetch_store=fetch_store,
        telegram_api_adapter=api_adapter,
        channel_handles=target_chats,
        start=last_fetched,
        end=end,
    )
    messages = fetch_store.load_messages_by_filename(message_file_path)
    last_fetched_str = last_fetched.isoformat()
    for message in messages:
        assert message.validate()
        assert message.channel_handle in target_chats
        assert message.time > last_fetched_str

    last_fetched_stored = fetch_store.load_last_fetch_times()
    assert last_fetched_stored is not None
    assert last_fetched_stored == end

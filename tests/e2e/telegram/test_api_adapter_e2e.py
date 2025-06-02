import logging
from typing import List
import pytest
from dropspy.telegram.api_adapter import TelegramAPIAdapter
from datetime import datetime, timedelta, timezone


@pytest.fixture
def api_adapter(pytestconfig):
    return TelegramAPIAdapter(
        api_id=pytestconfig.api_id,
        api_hash=pytestconfig.api_hash,
        session_name=pytestconfig.session,
    )


@pytest.fixture
def target_chats(pytestconfig) -> List[str]:
    return pytestconfig.target_chats


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_fetch_participating_channels_info_e2e(
    test_e2e_logger, api_adapter: TelegramAPIAdapter
):
    try:
        await api_adapter.connect()
        chans = await api_adapter.fetch_participating_channels_info()
        assert isinstance(chans, list)
        assert len(chans) > 0
        for chan in chans:
            assert chan.validate()
            test_e2e_logger.debug(
                "You are participating in: [handle: %s] [title: %s]",
                chan.handle,
                chan.title,
            )
        await api_adapter.disconnect()
    except RuntimeError as e:
        test_e2e_logger.error(e)
        pytest.fail(str(e))
    finally:
        await api_adapter.disconnect()


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize("days_interval", [1, 3])
async def test_fetch_messages_e2e(
    test_e2e_logger,
    api_adapter: TelegramAPIAdapter,
    target_chats: List[str],
    days_interval,
):
    if len(target_chats) == 0:
        pytest.skip("Skipping fetch_channel_messages test: no target chats specified")
    MAX_TARGET_CHATS = 3
    if len(target_chats) > MAX_TARGET_CHATS:
        target_chats = target_chats[:MAX_TARGET_CHATS]
    try:
        await api_adapter.connect()
        last_fetched_time = datetime.now(tz=timezone.utc) - timedelta(
            days=days_interval
        )
        last_fetched = [last_fetched_time] * len(target_chats)
        fetched = await api_adapter.fetch_messages(
            channel_handles=target_chats, last_fetch=last_fetched
        )
        for handle, messages in fetched.items():
            test_e2e_logger.debug(
                "Fetched messages from channel: %s / count: %d", handle, len(messages)
            )
            assert isinstance(messages, list)
            for msg in messages:
                assert msg.validate()
                assert msg.channel_handle == handle
                assert msg.date > last_fetched_time
    except RuntimeError as e:
        test_e2e_logger.error(e)
        pytest.fail(str(e))
    finally:
        await api_adapter.disconnect()

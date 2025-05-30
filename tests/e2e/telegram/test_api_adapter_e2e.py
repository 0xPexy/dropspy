import os
from typing import List
from dotenv import load_dotenv
import pytest
from dropspy.telegram.api_adapter import TelegramAPIAdapter
from datetime import datetime, timedelta, timezone
import asyncio

TEST_ENV_FILE = ".env.test"


@pytest.fixture(scope="session", autouse=True)
def load_env(pytestconfig):
    load_dotenv(TEST_ENV_FILE)
    pytestconfig.api_id = int(os.getenv("TELEGRAM_API_ID") or 0)
    pytestconfig.api_hash = os.getenv("TELEGRAM_API_HASH")
    pytestconfig.session = os.getenv("TELEGRAM_SESSION_NAME")
    pytestconfig.target_chats = []
    target_chats = os.getenv("TELEGRAM_TARGET_CHATS") or None
    if target_chats:
        pytestconfig.target_chats = [x.strip() for x in target_chats.split(",")]
    if not all([pytestconfig.api_id, pytestconfig.api_hash, pytestconfig.session]):
        pytest.skip("Skipping e2e test: missing required environment variables")


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


@pytest.mark.asyncio
async def test_fetch_participating_chats_info_e2e(api_adapter):
    await api_adapter.connect()
    chats = await api_adapter.fetch_participating_chats_info()
    assert isinstance(chats, list)
    assert len(chats) > 0
    for chat in chats:
        assert chat.validate()
    await api_adapter.disconnect()


@pytest.mark.asyncio
async def test_fetch_channel_messages_e2e(api_adapter, target_chats):
    if len(target_chats) == 0:
        pytest.skip("Skipping fetch_channel_messages test: no target chats specified")
    await api_adapter.connect()
    KST = timezone(timedelta(hours=9))
    last_fetch = datetime.now(tz=KST) - timedelta(days=1)
    for handle in target_chats:
        messages = await api_adapter.fetch_channel_messages(
            handle, after=last_fetch, limit=100
        )
        assert isinstance(messages, list)
        print(f"\n📥 Fetched messages channel: {handle} / from: {last_fetch.strftime('%Y-%m-%d %H:%M:%S %Z')} / count: {len(messages)}")
        for msg in messages:
            assert msg.validate()
    await api_adapter.disconnect()


@pytest.mark.asyncio
async def test_1(api_adapter, target_chats):
    if len(target_chats) == 0:
        pytest.skip("Skipping fetch_channel_messages test: no target chats specified")
    await api_adapter.connect()
    #await api_adapter.new_fetch(target_chats, datetime.now())
    await api_adapter.disconnect()


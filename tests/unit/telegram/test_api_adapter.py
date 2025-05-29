from datetime import datetime
import pytest
from unittest.mock import MagicMock, patch

from telegram.api_adapter import TelegramAPIAdapter
from telethon import TelegramClient


@pytest.fixture
def telegram_client():
    client = TelegramClient("none", 0, "none")
    client.connect = MagicMock(return_value=True)
    client.is_user_authorized = MagicMock(return_value=True)
    client.get_dialogs = MagicMock(return_value=[MagicMock()])
    client.get_entity = MagicMock(return_value=MagicMock())
    client.__call__ = MagicMock(return_value=MagicMock())
    return client


@pytest.fixture
def telegram_api_adapter(telegram_client):
    return TelegramAPIAdapter(0, "none", "none")


@patch("telegram.client.TelegramClient", return_value="client")
def test_fetch_participating_chats(telegram_client, telegram_api_adapter):
    assert telegram_api_adapter.client == "client"
    assert telegram_api_adapter.fetch_participating_chats_info() == [MagicMock()]


@patch("telegram.client.TelegramClient", return_value="client")
def test_fetch_channel_messages(telegram_client, telegram_api_adapter):
    assert telegram_api_adapter.client == "client"
    assert telegram_api_adapter.fetch_channel_messages("@test", datetime.now()) == [
        MagicMock()
    ]

from typing import Any, List, Dict, Tuple, Optional
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    InputPeerChannel,
    InputPeerUser,
    InputPeerChat,
    Channel,
    User,
    Chat,
)
from telethon.tl.custom import Dialog

"""TODO: use this in pipeline/fetch.py
from src.telegram.api_adapter import TelegramAPIAdapter
async with TelegramAPIAdapter(api_id, api_hash, session_name) as adapter:
    chat_list = await adapter.fetch_participating_chats()
    entity, messages = await adapter.fetch_channel_messages("@channel", since)
"""


class TelegramAPIAdapter:
    def __init__(self, api_id: int, api_hash: str, session_name: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None

    async def __aenter__(self):
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError("User not authorized.")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.disconnect()

    async def fetch_participating_chats(self) -> List[Dict[str, Any]]:
        try:
            if self.client is None:
                raise RuntimeError("Telegram client is not initialized.")
            dialogs = await self.client.get_dialogs()
            result = []
            for dialog in dialogs:
                result.append(self._process_chat_info(dialog))
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch participating chats: {e}")

    def _process_chat_info(self, dialog: Dialog) -> Dict[str, Any]:
        entity = dialog.entity
        chat_id = str(entity.id)
        title = getattr(entity, "title", "N/A")
        username = getattr(entity, "username", None)
        handle = f"@{username}" if username else None
        chat_info = {
            "id": chat_id,
            "title": title,
            "handle": handle,
        }
        return chat_info

    async def fetch_channel_messages(
        self, chat: str, since: datetime, limit: int = 100
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        try:
            if self.client is None:
                raise RuntimeError("Telegram client is not initialized.")
            entity = await self.client.get_entity(chat)
            if isinstance(entity, Channel):
                input_peer = InputPeerChannel(entity.id, entity.access_hash or 0)
            elif isinstance(entity, User):
                input_peer = InputPeerUser(entity.id, entity.access_hash or 0)
            elif isinstance(entity, Chat):
                input_peer = InputPeerChat(entity.id)
            else:
                raise ValueError("Unsupported entity type")
            messages = []
            offset_id = 0
            while True:
                history = await self.client(
                    GetHistoryRequest(
                        peer=input_peer,
                        limit=limit,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )
                if not hasattr(history, "messages") or not history.messages:
                    break
                for msg in history.messages:
                    if msg.date <= since:
                        messages.reverse()
                        return entity, messages
                    if getattr(msg, "message", None):
                        messages.append(
                            {
                                "id": msg.id,
                                "date": msg.date,
                                "text": msg.message.strip(),
                            }
                        )
                if len(history.messages) < limit:
                    break
                offset_id = history.messages[-1].id
            messages.reverse()
            return entity, messages
        except Exception as e:
            raise RuntimeError(f"Failed to fetch messages for {chat}: {e}")

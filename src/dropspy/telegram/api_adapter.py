from typing import Awaitable, Callable, List, Dict, Tuple, cast
from datetime import datetime
import logging
from dropspy.telegram.types import ChannelInfo, RawMessage
from telethon.sync import TelegramClient
from telethon.tl.types import (
    Channel,
    User,
    Chat,
    Message,
)
from telethon.tl.types.messages import Messages
from telethon.hints import Entity
from telethon.tl.custom import Dialog

class TelegramAPIAdapter:
    def __init__(
        self, api_id: int, api_hash: str, session_name: str, max_api_calls: int = 30
    ):
        self.client = TelegramClient(
            session=session_name, api_id=api_id, api_hash=api_hash
        )
        self.max_api_calls = max_api_calls

    async def connect(self):
        if not self.client.is_connected():
            await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError("User not authorized.")
        return self

    async def disconnect(self):
        if self.client.is_connected():
            disconnect = cast(Callable[[], Awaitable[None]], self.client.disconnect)
            await disconnect()

    async def fetch_participating_channels_info(self) -> List[ChannelInfo]:
        try:
            dialogs = await self.client.get_dialogs()
            result = []
            for dialog in dialogs:
                entity = dialog.entity
                if not isinstance(entity, Channel):
                    continue
                result.append(self._process_channel_info(entity))
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch participating chats: {e}")

    def _process_channel_info(self, entity: Channel) -> ChannelInfo:
        chat_info = ChannelInfo(
            id=entity.id,
            title=entity.title,
            handle=self._format_handle(entity.username),
        )
        return chat_info

    async def fetch_messages(
        self,
        channel_handles: List[str],
        last_fetch: List[datetime],
        limit_per_api_call: int = 100,
    ) -> Dict[str, List[RawMessage]]:
        try:
            fetched: Dict[str, List[RawMessage]] = dict()
            entities = await self._get_entities(channel_handles)
            for idx, entity in enumerate(entities):
                if not isinstance(entity, Channel):
                    continue
                messages = await self._fetch_messages(
                    entity, last_fetch[idx], limit_per_api_call
                )
                fetched[channel_handles[idx]] = messages
            return fetched
        except Exception as e:
            raise RuntimeError(f"Failed to fetch messages: {e}")

    async def _get_entities(self, channel_handles: List[str]) -> List[Entity]:
        entities = await self.client.get_entity(channel_handles)
        if isinstance(entities, Entity):
            entities = [entities]
        return entities

    async def _fetch_messages(
        self, channel_entity: Channel, last_fetch: datetime, limit: int
    ) -> List[RawMessage]:
        fetched = []
        trials = 0
        while True:
            end, messages = await self._fetch_loop(
                channel_entity=channel_entity, last_fetch=last_fetch, limit=limit
            )
            fetched.extend(messages)
            trials += 1
            if end or trials >= self.max_api_calls:
                break
        fetched.reverse()
        return fetched

    async def _fetch_loop(
        self, channel_entity: Channel, last_fetch: datetime, limit: int
    ) -> Tuple[bool, List[RawMessage]]:
        raw_messages: List[RawMessage] = []
        async for message in self.client.iter_messages(
            entity=channel_entity, limit=limit
        ):
            if not isinstance(message, Message) or message.date is None:
                continue
            if message.date <= last_fetch:
                return True, raw_messages
            raw_message = RawMessage(
                id=message.id,
                channel_id=channel_entity.id,
                channel_handle=self._format_handle(channel_entity.username),
                date=message.date,
                text=message.message.strip(),
            )
            raw_messages.append(raw_message)
        if len(raw_messages) < limit:
            return True, raw_messages
        return False, raw_messages

    def _format_handle(self, handle: str | None) -> str:
        return f"@{handle}" if handle else ""

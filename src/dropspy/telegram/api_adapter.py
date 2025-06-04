import logging
from typing import Awaitable, Callable, List, Dict, Tuple, cast
from datetime import datetime
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

logger = logging.getLogger(__name__)


class TelegramAPIAdapter:
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str,
        limit_per_api_call: int = 100,
        max_api_calls: int = 30,
    ):
        self.client = TelegramClient(
            session=session_name, api_id=api_id, api_hash=api_hash
        )
        self.limit_per_api_call = limit_per_api_call
        self.max_api_calls = max_api_calls

    async def connect(self):
        if not self.client.is_connected():
            await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError("User not authorized.")
        logger.info("Connected to Telegram API and authorized successfully")
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
            raise RuntimeError(e)

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
        last_fetch: datetime,
    ) -> List[RawMessage]:
        try:
            fetched: List[RawMessage] = []
            entities = await self._get_entities(channel_handles)
            for entity in entities:
                if not isinstance(entity, Channel):
                    continue
                logger.debug(
                    "Fetching messages from [%s](@%s)", entity.title, entity.username
                )
                messages = await self._fetch_messages(entity, last_fetch)
                logger.debug(
                    "Fetched %d messages from [%s](@%s)",
                    len(messages),
                    entity.title,
                    entity.username,
                )
                fetched.extend(messages)
            fetched.sort(key=lambda msg: msg.time)
            return fetched
        except Exception as e:
            raise RuntimeError(e)

    async def _get_entities(self, channel_handles: List[str]) -> List[Entity]:
        entities = await self.client.get_entity(channel_handles)
        if isinstance(entities, Entity):
            entities = [entities]
        return entities

    async def _fetch_messages(
        self, channel_entity: Channel, last_fetch: datetime
    ) -> List[RawMessage]:
        fetched = []
        trials = 0
        offset_id =0
        while True:
            end, messages = await self._fetch_loop(
                channel_entity=channel_entity,
                last_fetch=last_fetch,
                offset_id=offset_id,
                limit=self.limit_per_api_call,
            )
            fetched.extend(messages)
            offset_id = messages[-1].id
            trials += 1
            if end or trials >= self.max_api_calls:
                break
        return fetched

    async def _fetch_loop(
        self, channel_entity: Channel, last_fetch: datetime, offset_id:int, limit: int
    ) -> Tuple[bool, List[RawMessage]]:
        raw_messages: List[RawMessage] = []
        async for message in self.client.iter_messages(
            entity=channel_entity, offset_id=offset_id, limit=limit
        ):
            if not isinstance(message, Message) or message.date is None:
                continue
            if message.date <= last_fetch:
                return True, raw_messages
            raw_message = RawMessage(
                id=message.id,
                channel_id=channel_entity.id,
                channel_handle=self._format_handle(channel_entity.username),
                time=message.date.isoformat(),
                text=message.message.strip(),
            )
            raw_messages.append(raw_message)
        if len(raw_messages) < limit:
            return True, raw_messages
        return False, raw_messages

    def _format_handle(self, handle: str | None) -> str:
        return f"@{handle}" if handle else ""

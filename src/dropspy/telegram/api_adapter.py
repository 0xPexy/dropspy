from typing import Any, Awaitable, Callable, List, Dict, Tuple, Optional, cast
from datetime import datetime
import logging
from dropspy.telegram.types import ChatInfo, RawMessage
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    InputPeerChannel,
    InputPeerUser,
    InputPeerChat,
    Channel,
    User,
    Chat,
    TypeInputPeer,
    Message,
)
from telethon.tl.types.messages import Messages
from telethon.hints import Entity
from telethon.tl.custom import Dialog

logger = logging.getLogger(__name__)

class TelegramAPIAdapter:
    def __init__(self, api_id: int, api_hash: str, session_name: str):
        self.client = TelegramClient(
            session=session_name, api_id=api_id, api_hash=api_hash
        )

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

    async def fetch_participating_chats_info(self) -> List[ChatInfo]:
        if not self.client.is_connected():
            raise RuntimeError("Client not connected.")
        try:
            dialogs = await self.client.get_dialogs()
            result = []
            for dialog in dialogs:
                result.append(self._process_chat_info(dialog))
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch participating chats: {e}")

    def _process_chat_info(self, dialog: Dialog) -> ChatInfo:
        entity = dialog.entity
        chat_id = entity.id
        title = getattr(entity, "title", "N/A")
        username = getattr(entity, "username", None)
        handle = f"@{username}" if username else ""
        chat_info = ChatInfo(id=chat_id, title=title, handle=handle)
        return chat_info

    async def fetch_channel_messages(
        self, handle: str, after: datetime, limit: int = 100
    ) -> List[RawMessage]:
        try:
            if not self.client.is_connected():
                raise RuntimeError("Client not connected.")
            entity = await self.client.get_entity(handle)
            if not isinstance(entity, Entity):
                raise RuntimeError(f"Failed to get entity for {handle}")
            input_peer = self._get_input_peer(entity)
            messages = await self._fetch_messages_loop(
                input_peer=input_peer,
                channel_id=entity.id,
                channel_handle=handle,
                after=after,
                limit=limit,
            )
            return messages
        except Exception as e:
            raise RuntimeError(f"Failed to fetch messages for {handle}: {e}")

    async def new_fetch(
        self,
        channel_handles: List[str],
        last_fetch: datetime,
        limit_per_api_call: int = 100,
    ) -> List[RawMessage]:
        entities = await self._get_entities(channel_handles)
        logger.info(f"Entities: {entities}")
        return []

    async def _get_entities(self, channel_handles: List[str]) -> List[Entity]:
        entities = await self.client.get_entity(channel_handles)
        if isinstance(entities, Entity):
            entities = [entities]
        return entities

    async def _fetch_messages(self, channel_entity: Entity, limit: int):
        async for messages in self.client.iter_messages(
            entity=channel_entity, limit=limit
        ):
            if not isinstance(messages, Message) or messages.date is None:
                continue
            print(messages)

    async def _fetch_loop(
        self, channel_entity: Entity, last_fetch: datetime, limit: int
    ) -> Tuple[bool, List[RawMessage]]:
        raw_messages: List[RawMessage] = []
        async for message in self.client.iter_messages(
            entity=channel_entity, limit=limit
        ):
            if not isinstance(message, Message) or message.date is None:
                continue
            if message.date <= last_fetch:
                return True, raw_messages
            target_room = message.peer_id
            print(target_room)
            # target_room.channel_id
            # raw_meesage = RawMessage(
            #     id=message.id,
            #     channel_id=channel_entity.id,
            #     channel_handle=message.,
            #     time=message.date.isoformat(),
            #     text=message.message.strip(),
            # )
        return True, []

    # def _temp(self):
    #     raw_messages: List[RawMessage] = []
    #     async for msg in self.client.iter_messages(entity, limit=limit, reverse=False):
    #         if not isinstance(msg, Message) or msg.date is None:
    #             continue

    #         if msg.date <= after:
    #             break

    #         raw_msg = RawMessage(
    #             id=msg.id,
    #             channel_id=entity.id,
    #             channel_handle=handle,
    #             time=msg.date.isoformat(),
    #             text=msg.message.strip(),
    #         )
    #         raw_messages.append(raw_msg)

    #     raw_messages.reverse()  
    #     return raw_messages

    def _get_input_peer(
        self, entity: Entity
    ) -> InputPeerChannel | InputPeerUser | InputPeerChat:
        if isinstance(entity, Channel):
            return InputPeerChannel(entity.id, entity.access_hash or 0)
        elif isinstance(entity, User):
            return InputPeerUser(entity.id, entity.access_hash or 0)
        elif isinstance(entity, Chat):
            return InputPeerChat(entity.id)
        else:
            raise RuntimeError(f"Unsupported entity type: {type(entity)}")

    async def _fetch_messages_loop(
        self,
        input_peer: InputPeerChannel | InputPeerUser | InputPeerChat,
        channel_id: int,
        channel_handle: str,
        after: datetime,
        limit: int,
    ) -> List[RawMessage]:
        raw_messages: List[RawMessage] = []
        offset_id = 0
        while True:
            messages_by_offset = await self._get_messages_by_offset(
                input_peer, limit, offset_id
            )
            for msg in messages_by_offset.messages:
                if not isinstance(msg, Message) or msg.date is None:
                    continue

                if msg.date <= after:
                    raw_messages.reverse()
                    return raw_messages

                raw_msg = RawMessage(
                    id=msg.id,
                    channel_id=channel_id,
                    channel_handle=channel_handle,
                    time=msg.date.isoformat(),
                    text=msg.message.strip(),
                )
                raw_messages.append(raw_msg)

            if len(messages_by_offset.messages) < limit:
                break
            offset_id = messages_by_offset.messages[-1].id

        raw_messages.reverse()
        return raw_messages

    async def _get_messages_by_offset(
        self, input_peer: TypeInputPeer, limit: int, offset_id: int
    ) -> Messages:
        return await self.client(
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

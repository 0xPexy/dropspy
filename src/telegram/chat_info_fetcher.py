from telethon.sync import TelegramClient
from typing import List, Dict, Optional

class ChatInfoFetcher:
    def __init__(self, api_id: int, api_hash: str, session_name: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.chats: List[Dict] = []
        self.handle_to_id: Dict[str, str] = {}
        self.id_to_handle: Dict[str, str] = {}

    def fetch_participating_chats_info(self):
        with TelegramClient(self.session_name, self.api_id, self.api_hash) as client:
            dialogs = client.get_dialogs()
            result = []
            for dialog in dialogs:
                entity = dialog.entity
                chat_id = str(entity.id)
                title = getattr(entity, 'title', 'N/A')
                username = getattr(entity, 'username', None)
                handle = f"@{username}" if username else None

                chat_info = {
                    "id": chat_id,
                    "title": title,
                    "handle": handle,
                }
                result.append(chat_info)
                if handle:
                    self.handle_to_id[handle] = chat_id
                    self.id_to_handle[chat_id] = handle

            self.chats = result
            return result

    def get_id_by_handle(self, handle: str) -> Optional[str]:
        if not self.chats:
            self.fetch_participating_chats_info()
        return self.handle_to_id.get(handle)

    def get_handle_by_id(self, chat_id: str) -> Optional[str]:
        if not self.chats:
            self.fetch_participating_chats_info()
        return self.id_to_handle.get(chat_id)

    def get_chats_info(self) -> List[Dict]:
        if not self.chats:
            self.fetch_participating_chats_info()
        return self.chats
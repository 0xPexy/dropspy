# src/telegram/message_fetcher.py

import os
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

KST = timezone(timedelta(hours=9))


class MessageFetcher:
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str,
        target_chats: List[str],
        last_fetch_path: str,
        default_fetch_days: int = 7,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.target_chats = target_chats
        self.last_fetch_path = last_fetch_path
        self.default_fetch_days = default_fetch_days

    def _load_last_fetch_times(self) -> Dict[str, Dict[str, str]]:
        if os.path.exists(self.last_fetch_path):
            try:
                with open(self.last_fetch_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(
                    f"Warning: Invalid JSON in last fetch file: {self.last_fetch_path}. Ignoring and starting fresh."
                )
                return {}
        return {}

    def _save_last_fetch_times(self, last_fetch_times: Dict[str, Dict[str, str]]):
        os.makedirs(os.path.dirname(self.last_fetch_path), exist_ok=True)
        with open(self.last_fetch_path, "w") as f:
            json.dump(last_fetch_times, f, ensure_ascii=False, indent=2)

    def fetch(self, now: Optional[datetime] = None) -> List[Dict]:
        last_fetch_times = self._load_last_fetch_times()
        all_messages = []
        new_last_fetch = {}

        if now is None:
            now = datetime.now(KST)

        with TelegramClient(self.session_name, self.api_id, self.api_hash) as client:
            if not client.is_connected():
                client.connect()
            if not client.is_user_authorized():
                print(
                    "User is not authorized. Please run an interactive session first to log in."
                )
                return

            for chat in self.target_chats:
                print(f"\n📥 Fetching messages from: {chat}")
                entity = client.get_entity(chat)
                chat_id = str(entity.id)
                chat_handle = chat if chat.startswith("@") else entity.username or chat

                last_info = last_fetch_times.get(chat_id, {})
                if last_info and "last_fetch" in last_info:
                    since = datetime.fromisoformat(last_info["last_fetch"]).astimezone(
                        KST
                    )
                    print(
                        f"↪️ Resuming fetch since: {since.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                    )
                else:
                    since = now - timedelta(days=self.default_fetch_days)
                    print(
                        f"🆕 No previous record for '{chat}'. Fetching last {self.default_fetch_days} days (since {since.strftime('%Y-%m-%d %H:%M:%S %Z')})."
                    )

                messages = []
                offset_id = 0
                fetch_done = False
                while not fetch_done:
                    history = client(
                        GetHistoryRequest(
                            peer=entity,
                            limit=100,
                            offset_id=offset_id,
                            offset_date=None,
                            add_offset=0,
                            max_id=0,
                            min_id=0,
                            hash=0,
                        )
                    )
                    if not history.messages:
                        break

                    for msg in history.messages:
                        msg_time = msg.date.astimezone(KST)
                        if msg_time <= since:
                            fetch_done = True
                            break
                        if msg.message:
                            messages.append(
                                {
                                    "channel": chat,
                                    "time": msg_time.strftime("%Y-%m-%d %H:%M"),
                                    "text": msg.message.strip(),
                                }
                            )

                    if len(history.messages) < 100:
                        break
                    offset_id = history.messages[-1].id

                messages.reverse()
                print(f"✅ Collected {len(messages)} new messages from {chat}.")
                if messages:
                    all_messages.extend(messages)
                    new_last_fetch[chat_id] = {
                        "handle": chat_handle,
                        "last_fetch": messages[-1]["time"],
                    }
                elif chat_id in last_fetch_times:
                    prev = last_fetch_times[chat_id]
                    new_last_fetch[chat_id] = {
                        "handle": prev.get("handle", chat_handle),
                        "last_fetch": prev.get("last_fetch", ""),
                    }

        all_messages.sort(key=lambda m: m["time"])
        self._save_last_fetch_times(new_last_fetch)
        return all_messages

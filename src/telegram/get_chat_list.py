from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os

# 🔄 .env 로드
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME")

with TelegramClient(session_name, api_id, api_hash) as client:
    dialogs = client.get_dialogs()

    print("📋 내가 참여 중인 채팅방 리스트:\n")
    for dialog in dialogs:
        entity = dialog.entity
        title = getattr(entity, 'title', 'N/A')
        username = getattr(entity, 'username', None)
        if username:
            print(f"🆔 ID: {entity.id}")
            print(f"📛 Title: {title}")
            print(f"🔗 Username: @{username}")
            print("-" * 40)

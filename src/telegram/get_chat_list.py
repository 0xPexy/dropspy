from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os

def get_chat_list():
    load_dotenv()
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    session_name = os.getenv("SESSION_NAME")

    with TelegramClient(session_name, api_id, api_hash) as client:
        dialogs = client.get_dialogs()

        print("📋 List of Telegram chats I’m currently participating in:\n")
        for dialog in dialogs:
            entity = dialog.entity
            title = getattr(entity, 'title', 'N/A')
            username = getattr(entity, 'username', None)
            if username:
                print(f"🆔 ID: {entity.id}")
                print(f"📛 Title: {title}")
                print(f"🔗 Handle: @{username}")
                print("-" * 40)

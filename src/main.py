import argparse
from typing import List, Dict, Any
from telegram.chat_info_fetcher import ChatInfoFetcher
from config import (
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    TELEGRAM_DEFAULT_FETCH_DAYS,
    TELEGRAM_SESSION_NAME,
    TELEGRAM_TARGET_CHATS,
    PATH_FETCH_RECORD_FILE,
    PATH_CHAT_MESSAGES_DIR,
)
from telegram.message_fetcher import MessageFetcher
from telegram.message_store import MessageStore


def main():
    parser = argparse.ArgumentParser(description="DropSpy CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: chats
    subparsers.add_parser("chats", help="List currently joined Telegram chats")

    # Subcommand: fetch
    subparsers.add_parser("fetch", help="Fetch recent Telegram messages")

    args = parser.parse_args()

    if args.command == "chats":
        # Call the function to list Telegram chats
        fetcher = ChatInfoFetcher(
            TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME
        )
        chat_list = fetcher.get_chats_info()
        print_chats(chat_list)

    elif args.command == "fetch":
        # Call the function to fetch Telegram messages
        fetch_command()

    else:
        parser.print_help()


def fetch_command():
    try:
        fetcher = MessageFetcher(
            api_id=int(TELEGRAM_API_ID),
            api_hash=TELEGRAM_API_HASH,
            session_name=TELEGRAM_SESSION_NAME,
            target_chats=TELEGRAM_TARGET_CHATS,
            last_fetch_path=PATH_FETCH_RECORD_FILE,
            default_fetch_days=TELEGRAM_DEFAULT_FETCH_DAYS,
        )
        msgs = fetcher.fetch()
        print(f"Fetched {len(msgs)} messages.")
        store = MessageStore(PATH_CHAT_MESSAGES_DIR)
        path = store.save(msgs)
        print(f"Saved messages to {path}")
    # TODO: add more specific exceptions
    except Exception as e:
        print(f"An error occurred: {e}")


def print_chats(chats: List[Dict[str, Any]]):
    print("-" * 40)
    print("✉️ Participating Telegram Chats:")
    print("-" * 40)
    for chat in chats:
        print(f"🆔 ID: {chat['id']}")
        print(f"📛 Title: {chat['title']}")
        print(f"🔗 Handle: {chat['handle']}")
        print("-" * 40)


if __name__ == "__main__":
    main()

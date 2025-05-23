import argparse
from typing import List, Dict, Any
from telegram.chat_info_fetcher import ChatInfoFetcher
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME


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
        print("Fetch function is not yet implemented.")

    else:
        parser.print_help()


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

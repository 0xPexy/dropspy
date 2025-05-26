import argparse
import os
import shutil
import glob
from typing import List, Dict, Any
from telegram.chat_info_fetcher import ChatInfoFetcher
from config import (
    DATA_DIRECTORY_ROOT,
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    TELEGRAM_DEFAULT_FETCH_DAYS,
    TELEGRAM_SESSION_NAME,
    TELEGRAM_TARGET_CHATS,
    PATH_FETCH_RECORD_FILE,
    PATH_CHAT_MESSAGES_DIR,
    PATH_CHAT_PREBATCHES_DIR,
)
from telegram.message_fetcher import MessageFetcher
from telegram.message_store import MessageStore
from pipeline.prebatch import prebatch


def main():
    chat_info_fetcher = ChatInfoFetcher(
        TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME
    )
    message_fetcher = MessageFetcher(
        api_id=int(TELEGRAM_API_ID),
        api_hash=TELEGRAM_API_HASH,
        session_name=TELEGRAM_SESSION_NAME,
        target_chats=TELEGRAM_TARGET_CHATS,
        last_fetch_path=PATH_FETCH_RECORD_FILE,
        default_fetch_days=TELEGRAM_DEFAULT_FETCH_DAYS,
    )
    message_store = MessageStore(PATH_CHAT_MESSAGES_DIR)
    parser = argparse.ArgumentParser(description="DropSpy CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: chats
    subparsers.add_parser("chats", help="List currently joined Telegram chats")

    # Subcommand: fetch
    subparsers.add_parser("fetch", help="Fetch recent Telegram messages")

    prebatch_parser = subparsers.add_parser(
        "prebatch", help="Deduplicate and mark dup_count for a batch message file"
    )
    prebatch_parser.add_argument(
        "action", nargs="?", choices=["list"], help="Action to perform (list)"
    )
    prebatch_parser.add_argument(
        "--batch-index", type=int, default=0, help="Message file index to preprocess"
    )

    # Subcommand: batch
    batch_parser = subparsers.add_parser(
        "batch", help="Batch process saved message files"
    )
    batch_parser.add_argument(
        "action", nargs="?", choices=["list"], help="Action to perform (list)"
    )

    # Subcommand: reset
    subparsers.add_parser(
        "reset", help="Delete all app data in DATA_DIRECTORY_ROOT (dangerous!)"
    )

    args = parser.parse_args()

    if args.command == "chats":
        chats_command(chat_info_fetcher)

    elif args.command == "fetch":
        # Call the function to fetch Telegram messages
        fetch_command(message_fetcher=message_fetcher, message_store=message_store)

    elif args.command == "prebatch":
        if args.action == "list":
            message_store.print_file_list()
        else:
            prebatch_command(
                input_dir=PATH_CHAT_MESSAGES_DIR,
                output_dir=PATH_CHAT_PREBATCHES_DIR,
                batch_index=args.batch_index,
            )

    elif args.command == "batch":
        if args.action == "list":
            message_store.print_file_list()
        else:
            print("Provide an action. For now: 'list'")

    elif args.command == "reset":
        reset_data()

    else:
        parser.print_help()


def chats_command(chat_info_fetcher: ChatInfoFetcher):
    # Call the function to list Telegram chats
    chat_list = chat_info_fetcher.get_chats_info()
    print_chats(chat_list)


def print_chats(chats: List[Dict[str, Any]]):
    print("-" * 40)
    print("✉️ Participating Telegram Chats:")
    print("-" * 40)
    for chat in chats:
        print(f"🆔 ID: {chat['id']}")
        print(f"📛 Title: {chat['title']}")
        print(f"🔗 Handle: {chat['handle']}")
        print("-" * 40)


def fetch_command(message_fetcher: MessageFetcher, message_store: MessageStore):
    try:
        msgs = message_fetcher.fetch()
        print(f"Fetched {len(msgs)} messages.")
        path = message_store.save_messages(msgs)
        print(f"Saved messages to {path}")
    # TODO: add more specific exceptions
    except Exception as e:
        print(f"An error occurred: {e}")


def prebatch_command(input_dir: str, output_dir: str, batch_index: int = None):
    message_files = sorted(glob.glob(f"{input_dir}/*.json"))
    if not message_files:
        print(f"No message files found in {input_dir}")
        return
    if batch_index is None or batch_index < 0 or batch_index >= len(message_files):
        batch_index = 0
    target_file = message_files[batch_index]
    print(f"Pre-batching file: {target_file}")

    out_path = prebatch(target_file, output_dir)
    print(f"Pre-batched file saved to {out_path}")


def reset_data():
    data_dir = DATA_DIRECTORY_ROOT
    print(
        f"\n⚠️  WARNING: This will delete ALL data in '{data_dir}' and cannot be undone."
    )
    answer = input("Are you sure you want to continue? (yes/[no]): ").strip().lower()
    if answer != "yes":
        print("Aborted. No data was deleted.")
        return
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        print(f"✅ All data in '{data_dir}' has been removed.")
    else:
        print("No data directory found. Nothing to delete.")
    return


if __name__ == "__main__":
    main()

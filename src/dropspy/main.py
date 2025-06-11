import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import os
import shutil
from typing import List, Dict, Optional
from dropspy.config import (
    DATA_DIRECTORY_ROOT,
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    TELEGRAM_DEFAULT_FETCH_DAYS,
    TELEGRAM_SESSION_NAME,
    TELEGRAM_TARGET_CHATS,
    PATH_FETCH_RECORD_FILE,
    PATH_CHAT_MESSAGES_DIR,
    PATH_CHAT_PREBATCHES_DIR,
    LOGGING_CONFIG_PATH,
    APP_ENV,
)
from dropspy.pipeline.fetch import FetchStore, run_fetch_pipeline
from dropspy.pipeline.prebatch import PrebatchPipeline
from dropspy.telegram.api_adapter import TelegramAPIAdapter
from dropspy.telegram.types import ChannelInfo
from dropspy.utils.formatting import print_filename_with_index
from dropspy.utils.logging import cleanup_logging, setup_logging


def initialize_modules() -> tuple[TelegramAPIAdapter, FetchStore, PrebatchPipeline]:
    telegram_api_adapter = TelegramAPIAdapter(
        api_id=int(TELEGRAM_API_ID),
        api_hash=TELEGRAM_API_HASH,
        session_name=TELEGRAM_SESSION_NAME,
    )
    fetch_store = FetchStore(PATH_CHAT_MESSAGES_DIR)
    prebatch_pipeline = PrebatchPipeline(PATH_CHAT_PREBATCHES_DIR)
    return telegram_api_adapter, fetch_store, prebatch_pipeline


def setup_cli():
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

    return parser


async def execute_command(
    parser: argparse.ArgumentParser,
    telegram_api_adapter: TelegramAPIAdapter,
    fetch_store: FetchStore,
    prebatch_pipeline: PrebatchPipeline,
):
    args = parser.parse_args()
    if args.command == "chats":
        await chats_command(telegram_api_adapter=telegram_api_adapter)

    elif args.command == "fetch":
        await fetch_command(
            telegram_api_adapter=telegram_api_adapter, fetch_store=fetch_store
        )

    elif args.command == "prebatch":
        if args.action == "list":
            fetches = fetch_store.get_filenames()
            print_filename_with_index(fetches)
        else:
            messages = fetch_store.get_file_by_index(args.batch_index)
            prebatch_command(
                prebatch_pipeline=prebatch_pipeline,
                input_filename=messages["filename"],
                fetched_messages=messages["content"],
            )

    elif args.command == "batch":
        if args.action == "list":
            prebatches = prebatch_pipeline.prebatchStore.get_filenames()
            print_filename_with_index(prebatches)
        else:
            print("Provide an action. For now: 'list'")

    elif args.command == "reset":
        reset_data()

    else:
        parser.print_help()


async def main():
    telegram_api_adapter: Optional[TelegramAPIAdapter] = None
    try:
        setup_logging(LOGGING_CONFIG_PATH)
        telegram_api_adapter, fetch_store, prebatch_pipeline = initialize_modules()
        parser = setup_cli()
        await telegram_api_adapter.connect()
        await execute_command(
            parser=parser,
            telegram_api_adapter=telegram_api_adapter,
            fetch_store=fetch_store,
            prebatch_pipeline=prebatch_pipeline,
        )
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cleanup_logging()
        if telegram_api_adapter is not None:
            await telegram_api_adapter.disconnect()


async def chats_command(telegram_api_adapter: TelegramAPIAdapter):
    # Call the function to list Telegram chats
    channels = await telegram_api_adapter.fetch_participating_channels_info()
    print_chats(channels)


def print_chats(channels: List[ChannelInfo]):
    print("-" * 40)
    print("✉️ Participating Telegram Chats:")
    print("-" * 40)
    for channel in channels:
        print(f"🆔 ID: {channel.id}")
        print(f"📛 Title: {channel.title}")
        print(f"🔗 Handle: {channel.handle}")
        print("-" * 40)


async def fetch_command(
    telegram_api_adapter: TelegramAPIAdapter, fetch_store: FetchStore
):
    now = datetime.now(tz=timezone.utc)
    last_fetched = fetch_store.load_last_fetch_times() or now - timedelta(
        days=TELEGRAM_DEFAULT_FETCH_DAYS
    )
    message_file_path = await run_fetch_pipeline(
        fetch_store=fetch_store,
        telegram_api_adapter=telegram_api_adapter,
        channel_handles=TELEGRAM_TARGET_CHATS,
        start=last_fetched,
        end=now,
    )
    print(f"Saved messages to {message_file_path}")


def prebatch_command(
    prebatch_pipeline: PrebatchPipeline, input_filename: str, fetched_messages: Dict
):
    try:
        print(f"Pre-batching file: {input_filename}")
        out_path = prebatch_pipeline.run_prebatch_pipeline(
            input_filename, fetched_messages
        )
        print(f"Pre-batched file saved to {out_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return


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
    asyncio.run(main())

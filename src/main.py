import argparse
#from telegram.fetch_messages import fetch_messages
from telegram.get_chat_list import get_chat_list
# from digest.gemini_digest import generate_digest  # To be implemented

def main():
    parser = argparse.ArgumentParser(description="DropSpy CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: fetch
    subparsers.add_parser("fetch", help="Fetch recent Telegram messages")

    # Subcommand: chat-list
    subparsers.add_parser("chat-list", help="List currently joined Telegram chats")

    # Subcommand: digest
    subparsers.add_parser("digest", help="Generate AI-based digest from collected messages")

    args = parser.parse_args()

    if args.command == "fetch":
        # Call the function to fetch Telegram messages
        #fetch_messages()
        print("Message fetching is not yet implemented.")

    elif args.command == "chat-list":
        # Call the function to list Telegram chats
        get_chat_list()

    elif args.command == "digest":
        # Call the function to generate digest (to be implemented)
        print("Digest generation is not yet implemented.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

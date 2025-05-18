from dotenv import dotenv_values

config = dotenv_values(".env")

API_ID = int(config["API_ID"])
API_HASH = config["API_HASH"]
SESSION_NAME = config["SESSION_NAME"]

# @ 포함 입력 허용하되 내부적으로는 제거
TARGET_CHATS = [chat.strip().lstrip("@") for chat in config["TARGET_CHATS"].split(",")]
DEFAULT_FETCH_DAYS = int(config.get("DEFAULT_FETCH_DAYS", 3))
PROMPT_VERSION = config.get("PROMPT_VERSION", "v1.0")
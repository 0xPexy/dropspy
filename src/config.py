# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram API Credentials & Settings ---
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "default_telegram_session")
_target_chats_str = os.getenv("TELEGRAM_TARGET_CHATS", "")
TELEGRAM_TARGET_CHATS = [
    chat.strip() for chat in _target_chats_str.split(",") if chat.strip()
]
TELEGRAM_DEFAULT_FETCH_DAYS = int(os.getenv("TELEGRAM_DEFAULT_FETCH_DAYS", "7"))

# --- Google Generative AI API Settings ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Model Configurations for DropSpy ---
LIGHTWEIGHT_MODEL_NAME = os.getenv("LIGHTWEIGHT_MODEL_NAME", "gemini-2.0-flash-lite")
LIGHTWEIGHT_MODEL_CONTEXT_WINDOW_SIZE = int(
    os.getenv("LIGHTWEIGHT_MODEL_CONTEXT_WINDOW_SIZE", "1000000")
)
BATCH_TARGET_WINDOW_PERCENTAGE = float(
    os.getenv("BATCH_TARGET_WINDOW_PERCENTAGE", "0.80")
)

# Optional: Model for final, more complex analysis
FINAL_ANALYSIS_MODEL_NAME = os.getenv(
    "FINAL_ANALYSIS_MODEL_NAME"
)  # Defaults to None if not set

# --- File Paths and Directories ---
DATA_DIRECTORY_ROOT = os.getenv("DATA_DIRECTORY_ROOT", "data")
# FIRST_PASS_PROMPT_FILE_PATH = os.getenv(
#     "FIRST_PASS_PROMPT_FILE_PATH", "prompts/1st_pass_filter_prompt.md"
# )

# # Optional: Paths for other prompt files
# SECOND_PASS_PROMPT_FILE_PATH = os.getenv("SECOND_PASS_PROMPT_FILE_PATH")
# FINAL_ANALYSIS_PROMPT_FILE_PATH = os.getenv("FINAL_ANALYSIS_PROMPT_FILE_PATH")

# Internal constants for subdirectories and filenames derived from DATA_DIRECTORY_ROOT
_CHAT_BATCHES_SUBDIR_NAME = "chat_batches"
_FETCH_RECORD_FILENAME_ONLY = "last_fetch.json"
_LOG_SUBDIR_NAME = "logs"  # Example for logs, if you add logging


def get_data_path(filename_or_subdir: str) -> str:
    """Constructs a full path within the DATA_DIRECTORY_ROOT."""
    return os.path.join(DATA_DIRECTORY_ROOT, filename_or_subdir)

PATH_CHAT_BATCHES_DIR = get_data_path(_CHAT_BATCHES_SUBDIR_NAME)
PATH_FETCH_RECORD_FILE = get_data_path(_FETCH_RECORD_FILENAME_ONLY)
PATH_LOG_DIR = get_data_path(_LOG_SUBDIR_NAME)  # Example for logs

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
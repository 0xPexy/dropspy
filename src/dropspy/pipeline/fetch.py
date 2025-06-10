import logging
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta, timezone
from dropspy.telegram.api_adapter import TelegramAPIAdapter
from dropspy.telegram.types import RawMessage
from dropspy.utils.json_store import JSONStore
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FetchStore(JSONStore):
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.LAST_FETCH_KEY = "last_fetch"
        self.last_fetch_data_filename = f"{self.LAST_FETCH_KEY}.json"

    def save_messages(self, filename: str, messages: List[RawMessage]) -> str:
        return self._save(filename, messages)

    def load_messages_by_filename(self, filename: str) -> List[RawMessage]:
        messages = self._load(filename) or []
        return [RawMessage(**message) for message in messages]

    def load_last_fetch_times(self) -> datetime | None:
        last_fetch_file = self._load(self.last_fetch_data_filename) or {}
        last_fetch = last_fetch_file.get(self.LAST_FETCH_KEY, None)
        if last_fetch is None:
            return None
        logger.info("Last fetch time: %s", last_fetch)
        return datetime.fromisoformat(last_fetch)

    def save_last_fetch_times(self, last_fetch: datetime):
        data = {self.LAST_FETCH_KEY: last_fetch.isoformat()}
        return self._save(self.last_fetch_data_filename, data)

    def get_filenames(self):
        files = [f for f in self._list_files() if f != self.last_fetch_data_filename]
        return files


async def run_fetch_pipeline(
    fetch_store: FetchStore,
    telegram_api_adapter: TelegramAPIAdapter,
    channel_handles: List[str],
    start: datetime,
    end: datetime,
) -> str:
    try:
        logger.debug(
            "Running fetch pipeline: %s ~ %s", start.isoformat(), end.isoformat()
        )
        messages = await telegram_api_adapter.fetch_messages(channel_handles, start)
        logger.debug("Fetched total %d messages from channels", len(messages))
        filename = _make_messages_filename(start.isoformat(), end.isoformat())
        message_file = fetch_store.save_messages(filename, messages)
        fetch_store.save_last_fetch_times(end)
        logger.debug("Saved messages to %s", message_file)
        return message_file
    except Exception as e:
        raise RuntimeError(e)


def _make_messages_filename(start: str, end: str) -> str:
    return f"{start}~{end}.json"

from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
import json


@dataclass
class ChatInfo:
    id: int
    title: str
    handle: str

    def validate(self) -> bool:
        try:
            assert isinstance(self.id, int)
            assert isinstance(self.title, str)
            assert isinstance(self.handle, str)
            return True
        except AssertionError:
            return False


@dataclass
class RawMessage:
    id: int
    channel_id: int
    channel_handle: str
    time: str  # ISO format string
    text: str

    def validate(self) -> bool:
        try:
            assert isinstance(self.id, int)
            assert isinstance(self.channel_id, int)
            assert isinstance(self.channel_handle, str)
            # Validate ISO datetime format
            datetime.fromisoformat(self.time)
            assert isinstance(self.text, str)
            return True
        except (AssertionError, ValueError):
            return False

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, data: str) -> RawMessage:
        obj = json.loads(data)
        return cls(**obj)

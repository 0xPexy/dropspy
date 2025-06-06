from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
import json


@dataclass
class ChannelInfo:
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
    time: str
    text: str

    def validate(self) -> bool:
        try:
            assert isinstance(self.id, int)
            assert isinstance(self.channel_id, int)
            assert isinstance(self.channel_handle, str)
            assert isinstance(self.time, str)
            datetime.fromisoformat(self.time)
            assert isinstance(self.text, str)
            return True
        except (AssertionError, ValueError):
            return False

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: str) -> RawMessage:
        obj = json.loads(data)
        return cls(**obj)

import pytest
import os
import json
from tempfile import TemporaryDirectory
from telegram.message_store import MessageStore

@pytest.fixture
def message_store():
    with TemporaryDirectory() as temp_dir:
        yield MessageStore(temp_dir)

def test_save_and_load_messages(message_store):
    messages = [
        {"channel": "@chan1", "time": "2023-10-01 10:00", "text": "Hello World!"},
        {"channel": "@chan1", "time": "2023-10-01 10:05", "text": "Another message"}
    ]
    # Test saving messages
    saved_path = message_store.save_messages(messages)
    assert os.path.exists(saved_path)

    # Test loading messages
    loaded_messages = message_store.load_messages(os.path.basename(saved_path))
    assert loaded_messages == messages

def test_save_messages_empty(message_store):
    with pytest.raises(ValueError, match="No messages to save."):
        message_store.save_messages([])


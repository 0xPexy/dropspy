import logging
import tempfile
from typing import List
import pytest
import os
from dotenv import load_dotenv
from dropspy.config import LOGGER_PREFIX
from dropspy.telegram.api_adapter import TelegramAPIAdapter

E2E_TEST_ENV_FILE = ".env.test"
LOGGER_NAME = LOGGER_PREFIX + ".tests.e2e"


@pytest.fixture(scope="session")
def test_e2e_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


@pytest.fixture(scope="session", autouse=True)
def load_env(test_e2e_logger, pytestconfig):
    test_e2e_logger.debug("Loading environment variables from %s", E2E_TEST_ENV_FILE)
    load_dotenv(E2E_TEST_ENV_FILE)
    pytestconfig.api_id = int(os.getenv("TELEGRAM_API_ID") or 0)
    pytestconfig.api_hash = os.getenv("TELEGRAM_API_HASH") or None
    pytestconfig.session = os.getenv("TELEGRAM_SESSION_NAME") or None
    pytestconfig.target_chats = []
    target_chats = os.getenv("TELEGRAM_TARGET_CHATS") or None
    if target_chats:
        pytestconfig.target_chats = [x.strip() for x in target_chats.split(",")]
    if not all([pytestconfig.api_id, pytestconfig.api_hash, pytestconfig.session]):
        pytest.skip("Skipping e2e test: missing required environment variables")


@pytest.fixture
def api_adapter(pytestconfig):
    return TelegramAPIAdapter(
        api_id=pytestconfig.api_id,
        api_hash=pytestconfig.api_hash,
        session_name=pytestconfig.session,
    )


@pytest.fixture
def target_chats(pytestconfig) -> List[str]:
    return pytestconfig.target_chats


@pytest.fixture
def tmp_last_fetch_file():
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def tmp_msg_dir():
    d = tempfile.TemporaryDirectory()
    yield d.name
    d.cleanup()


@pytest.fixture
def tmp_prebatch_dir():
    d = tempfile.TemporaryDirectory()
    yield d.name
    d.cleanup()


@pytest.fixture
def tmp_batch_dir():
    d = tempfile.TemporaryDirectory()
    yield d.name
    d.cleanup()

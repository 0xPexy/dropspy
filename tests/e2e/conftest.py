import logging
import pytest
import os
from dotenv import load_dotenv

from dropspy.config import LOGGER_PREFIX

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

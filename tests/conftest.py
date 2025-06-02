import logging
import os
import pytest

from dropspy.config import LOGGER_PREFIX
from dropspy.utils.logging import cleanup_logging, setup_logging

TEST_LOGGER = LOGGER_PREFIX + ".tests"
logger = logging.getLogger()


@pytest.fixture(scope="session", autouse=True)
def configure_logging_for_tests():
    setup_logging()
    logger.info("Configured logging for tests")

    yield
    cleanup_logging()
    logger.info("Cleaned up logging for tests")

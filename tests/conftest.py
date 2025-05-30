import logging
import logging.config
import os
import pytest

from dropspy.utils.logging import setup_logging

LOGGING_CONFIG_PATH = "./config/logging.yaml"
DROPSPY_PREFIX = "dropspy"
TEST_LOGGER_NAME = DROPSPY_PREFIX + ".test"


class DropspyModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith(DROPSPY_PREFIX)


@pytest.fixture(scope="session", autouse=True)
def configure_logging_for_tests():
    setup_logging(LOGGING_CONFIG_PATH)
    test_logger = logging.getLogger(TEST_LOGGER_NAME)
    test_logger.info("Configuring logging for tests")
    root_logger = logging.getLogger()

    source_filter = DropspyModuleFilter()

    for handler in root_logger.handlers:
        handler.addFilter(source_filter)

    yield
    test_logger.info("Cleaning up logging for tests")
    for handler in root_logger.handlers:
        if source_filter in handler.filters:
            handler.removeFilter(source_filter)


@pytest.fixture
def test_logger():
    return logging.getLogger(TEST_LOGGER_NAME)

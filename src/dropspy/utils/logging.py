import logging.config
import yaml
from dropspy.config import LOGGER_PREFIX, LOGGING_CONFIG_PATH


class DropspyModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith(LOGGER_PREFIX)


def setup_logging(config_path: str = LOGGING_CONFIG_PATH):
    # Load the logging configuration
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)

    root_logger = logging.getLogger()
    # Add a filter to only log messages from the dropspy module
    source_filter = DropspyModuleFilter()

    for handler in root_logger.handlers:
        handler.addFilter(source_filter)


def cleanup_logging():
    root_logger = logging.getLogger()
    source_filter = DropspyModuleFilter()
    for handler in root_logger.handlers:
        if source_filter in handler.filters:
            handler.removeFilter(source_filter)




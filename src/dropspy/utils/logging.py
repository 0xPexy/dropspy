import logging.config
import os
import yaml
from pathlib import Path
from dropspy.config import (
    LOGGER_PREFIX,
    LOGGING_CONFIG_PATH,
    PATH_LOG_DIR,
    LOG_FILE_NAME,
    APP_ENV,
)


class DropspyModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith(LOGGER_PREFIX)


def create_log_directory():
    os.makedirs(PATH_LOG_DIR, exist_ok=True)
    return Path(PATH_LOG_DIR) / LOG_FILE_NAME


def setup_logging(config_path: str = LOGGING_CONFIG_PATH):
    log_file_path = create_log_directory()

    # Load the logging configuration
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Set file handler path dynamically
    for handler in config["handlers"].values():
        if "filename" in handler:
            handler["filename"] = str(log_file_path)

    # 환경별 핸들러 및 로그 레벨 구성
    if "loggers" in config:
        if APP_ENV == "development":
            # 개발 환경: 모든 로거에 devConsoleHandler 사용, DEBUG 레벨
            for logger_name, logger_config in config["loggers"].items():
                logger_config["handlers"] = ["devConsoleHandler"]
                logger_config["level"] = "DEBUG"
        else:
            # 프로덕션 환경: 모든 로거에 fileHandler 사용, INFO 레벨
            for logger_name, logger_config in config["loggers"].items():
                logger_config["handlers"] = ["fileHandler"]
                logger_config["level"] = "INFO"
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

import logging.config
import yaml
from pathlib import Path

def setup_logging(config_path: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)

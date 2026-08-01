import logging
from datetime import datetime
from pathlib import Path

from src.common.config import config


def get_logger():

    # Create logs folder if it doesn't exist
    log_folder = Path(config.log_path)
    log_folder.mkdir(parents=True, exist_ok=True)

    # Log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = log_folder / f"run_ListenBrainz_main_{timestamp}.log"

    # Configure logger
    logger = logging.getLogger("ListenBrainz")

    # Prevent duplicate handlers if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(getattr(logging, config.log_level.upper()))

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("=" * 60)
    logger.info("ListenBrainz ETL Started")
    logger.info("=" * 60)

    return logger
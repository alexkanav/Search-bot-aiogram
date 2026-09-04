import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import MAX_LOG_SIZE, LOG_BACKUP_COUNT


def configure_logging(log_path: Path, level: int = logging.INFO) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

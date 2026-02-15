import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

app_log = logging.getLogger("RadarAppLogger")


def setup_logging(logfile_name: str = "app"):
    """Configure global logger with file (prod) or console (dev)."""
    env = str(os.environ.get("ENV", "prod")).lower()  # default 'prod'
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{logfile_name}.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s(%(lineno)d) | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # Remove old handlers to avoid duplicate logs
    app_log.handlers.clear()

    if env == "dev":
        # Console logging in development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        app_log.setLevel(logging.DEBUG)
        app_log.addHandler(console_handler)
    else:
        # Rotating file logs in production
        file_handler = RotatingFileHandler(
            log_file, mode="a", maxBytes=5 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app_log.setLevel(logging.INFO)
        app_log.addHandler(file_handler)


def log_info(message: str):
    app_log.info(message)


def log_error(message: str):
    app_log.error(message)


def log_debug(message: str):
    app_log.debug(message)

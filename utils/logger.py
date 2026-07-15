"""Logging configuration for the Multi-Agent AI Chatbot.

Uses the Python standard library logging module only. Configuration is
driven by environment variables.

Environment Variables:
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR) — default: INFO
    LOG_FORMAT: Output format ("text" or "json") — default: text
    LOG_FILE: Optional path for rotating log file (max 10MB, 5 backups)
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Any


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "text")
LOG_FILE = os.getenv("LOG_FILE", "")


class _JsonFormatter(logging.Formatter):
    """JSON log formatter emitting timestamp, level, name, message and exc_info."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def _get_log_level() -> int:
    """Convert the LOG_LEVEL string to a logging module level."""
    return getattr(logging, LOG_LEVEL.upper(), logging.INFO)


def _create_formatter() -> logging.Formatter:
    """Create the formatter selected by LOG_FORMAT."""
    if LOG_FORMAT.lower() == "json":
        return _JsonFormatter()

    return logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )


def setup_logging() -> None:
    """Configure the root logger for the application.

    Called once at startup from backend/main.py. Idempotent — safe to call
    multiple times.
    """
    root_logger = logging.getLogger()

    # Avoid duplicate handlers when called more than once.
    if root_logger.handlers:
        return

    root_logger.setLevel(_get_log_level())
    formatter = _create_formatter()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    for name in (
        "httpx",
        "httpcore",
        "urllib3",
        "google",
        "google.auth",
        "google.generativeai",
        "multipart",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)

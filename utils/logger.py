"""Logging helpers for the Multi-Agent AI Chatbot."""

import logging


def setup_logging() -> None:
    """Configure root logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )


def get_logger(name: str):
    """Return a logger for the given module name."""
    return logging.getLogger(name)

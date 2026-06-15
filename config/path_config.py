"""Filesystem path configuration."""

import os
from typing import Final

BASE_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: Final[str] = os.path.join(BASE_DIR, "..", "data")
EAMCET_CSV: Final[str] = os.path.join(DATA_DIR, "eamcet_data.csv")
UPLOAD_DIR: Final[str] = os.path.join(BASE_DIR, "..", "uploads")


def ensure_directories() -> None:
    """Create filesystem directories required by the application."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

__all__ = ["BASE_DIR", "DATA_DIR", "EAMCET_CSV", "UPLOAD_DIR", "ensure_directories"]
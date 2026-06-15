"""LLM configuration constants."""

import os
from typing import Final

OLLAMA_URL: Final[str] = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL: Final[str] = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_TIMEOUT: Final[int] = int(os.getenv("OLLAMA_TIMEOUT", "240"))

__all__ = ["OLLAMA_URL", "OLLAMA_MODEL", "OLLAMA_TIMEOUT"]
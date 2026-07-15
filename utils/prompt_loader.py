import os
from functools import lru_cache
from utils.logger import get_logger

logger = get_logger(__name__)

# Determine if we are in development mode
IS_DEV = os.getenv("ENV", "production").lower() in ("development", "dev")

@lru_cache(maxsize=32)
def _load_prompt_cached(filename: str) -> str:
    """
    Loads a prompt template from the backend/prompts directory.
    Results are cached in memory for fast repeated access.
    """
    prompt_path = os.path.join("backend", "prompts", filename)
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Prompt template {filename} not found.")
        return ""
    except Exception as e:
        logger.error(f"Failed to read {filename}: {e}")
        return ""

def load_prompt(filename: str) -> str:
    """
    Loads a prompt template.
    Bypasses the cache and reads directly from disk if in development mode.
    """
    if IS_DEV:
        return _load_prompt_cached.__wrapped__(filename)
    return _load_prompt_cached(filename)

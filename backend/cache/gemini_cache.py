import sqlite3
import hashlib
import time
import os
import re
import threading
from config.path_config import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = os.path.join(DATA_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_DB = os.path.join(CACHE_DIR, "gemini_cache.db")

# Cache version for invalidation on normalization changes
CACHE_VERSION = "v1"

# Pre-compiled regex for whitespace normalization
_WHITESPACE_RE = re.compile(r'[ \t]+')


class GeminiCache:
    def __init__(self, db_path=CACHE_DB):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
        self.purge_expired()

    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        expires_at REAL
                    )
                """)
                conn.commit()

    def _hash_key(self, prompt: str, model: str) -> str:
        # 1. Strip leading/trailing whitespace
        norm_prompt = prompt.strip()

        # 2. Normalize line endings
        norm_prompt = norm_prompt.replace("\r\n", "\n")

        # 3. Collapse multiple spaces/tabs to single space (preserve newlines)
        norm_prompt = _WHITESPACE_RE.sub(' ', norm_prompt)

        # 4. Full lowercase for consistency
        norm_prompt = norm_prompt.lower()

        # 5. Extract domain prefix if present (e.g., "career:..." -> domain + rest)
        #    After lowercasing, domain prefix is already normalized
        parts = norm_prompt.split(":", 1)
        if len(parts) == 2 and not any(c.isspace() for c in parts[0]):
            # Valid domain prefix detected, keep as-is
            domain = parts[0]
            query = parts[1].lstrip()
            norm_prompt = f"{domain}:{query}"
        # else: no valid domain prefix, use full normalized string

        # Include cache version for future invalidation
        s = f"{CACHE_VERSION}::{model}::{norm_prompt}".encode("utf-8")
        return hashlib.sha256(s).hexdigest()

    def get(self, prompt: str, model: str) -> str | None:
        key = self._hash_key(prompt, model)
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,))
                row = cur.fetchone()
                if row:
                    value, expires_at = row
                    if time.time() < expires_at:
                        return value
                    else:
                        cur.execute("DELETE FROM cache WHERE key = ?", (key,))
                        conn.commit()
        return None

    def set(self, prompt: str, model: str, result: str, ttl: int) -> None:
        key = self._hash_key(prompt, model)
        expires_at = time.time() + ttl
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache (key, value, expires_at)
                    VALUES (?, ?, ?)
                """, (key, result, expires_at))
                conn.commit()

    def purge_expired(self) -> None:
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
                conn.commit()
        logger.info("Purged expired cache entries.")

    def get_stats(self) -> dict:
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM cache")
                total = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM cache WHERE expires_at > ?", (time.time(),))
                active = cur.fetchone()[0]
        return {
            "total_keys_ever": total,
            "active_keys": active,
            "expired_keys": total - active
        }

gemini_cache = GeminiCache()
import sqlite3
import datetime
import os
import threading
from config.path_config import DATA_DIR
from config.ai_features import FLASH_DAILY_LIMIT, PRO_DAILY_LIMIT
from utils.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = os.path.join(DATA_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
USAGE_DB = os.path.join(CACHE_DIR, "usage.db")

TIERS = {
    "flash": FLASH_DAILY_LIMIT,
    "pro": PRO_DAILY_LIMIT,
}

class UsageTracker:
    def __init__(self, db_path=USAGE_DB):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS usage (
                        username TEXT,
                        date TEXT,
                        tier TEXT,
                        count INTEGER,
                        PRIMARY KEY (username, date, tier)
                    );
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        timestamp TEXT,
                        route TEXT,
                        pipeline TEXT,
                        provider TEXT,
                        latency REAL,
                        status TEXT,
                        event_name TEXT
                    );
                    CREATE TABLE IF NOT EXISTS api_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint TEXT,
                        latency REAL,
                        status_code INTEGER,
                        timestamp TEXT
                    );
                    CREATE TABLE IF NOT EXISTS pipeline_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pipeline_name TEXT,
                        success BOOLEAN,
                        timestamp TEXT
                    );
                    CREATE TABLE IF NOT EXISTS daily_metrics (
                        date TEXT PRIMARY KEY,
                        active_users INTEGER,
                        total_requests INTEGER
                    );
                """)
                conn.commit()

    def _get_today(self) -> str:
        # Resets at midnight UTC
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    def can_use(self, username: str, tier: str = "flash") -> bool:
        today = self._get_today()
        limit = TIERS.get(tier, 0)
        if limit <= 0:
            return False

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT count FROM usage WHERE username = ? AND date = ? AND tier = ?",
                    (username, today, tier)
                )
                row = cur.fetchone()
                count = row[0] if row else 0
                return count < limit

    def record_use(self, username: str, tier: str = "flash") -> None:
        today = self._get_today()
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO usage (username, date, tier, count)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(username, date, tier) DO UPDATE SET count = count + 1
                """, (username, today, tier))
                conn.commit()

    def get_remaining(self, username: str) -> dict[str, int]:
        today = self._get_today()
        remaining = {}
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                for tier, limit in TIERS.items():
                    cur.execute(
                        "SELECT count FROM usage WHERE username = ? AND date = ? AND tier = ?",
                        (username, today, tier)
                    )
                    row = cur.fetchone()
                    count = row[0] if row else 0
                    remaining[tier] = max(0, limit - count)
        return remaining

    def get_stats(self) -> dict:
        today = self._get_today()
        flash_today = {}
        pro_today = {}
        total_events_today = 0
        events_by_route = {}
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                # Flash usage today per user
                cur.execute("SELECT username, count FROM usage WHERE date = ? AND tier = ?", (today, "flash"))
                for row in cur.fetchall():
                    flash_today[row[0]] = row[1]
                # Pro usage today per user
                cur.execute("SELECT username, count FROM usage WHERE date = ? AND tier = ?", (today, "pro"))
                for row in cur.fetchall():
                    pro_today[row[0]] = row[1]
                # Total events today
                cur.execute("SELECT COUNT(*) FROM events WHERE timestamp LIKE ?", (f"{today}%",))
                total_events_today = cur.fetchone()[0]
                # Events by route today
                cur.execute("SELECT route, COUNT(*) FROM events WHERE timestamp LIKE ? AND route IS NOT NULL AND route != '' GROUP BY route", (f"{today}%",))
                for row in cur.fetchall():
                    events_by_route[row[0]] = row[1]
        return {
            "flash_today": flash_today,
            "pro_today": pro_today,
            "total_events_today": total_events_today,
            "events_by_route": events_by_route,
        }

    def track_event(self, username: str, event_name: str, route: str = "", pipeline: str = "",
                    provider: str = "", latency: float = 0.0, status: str = "success") -> None:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO events (username, timestamp, route, pipeline, provider, latency, status, event_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, timestamp, route, pipeline, provider, latency, status, event_name))
                conn.commit()
        logger.debug("Tracked event | user=%s event=%s route=%s", username, event_name, route)

usage_tracker = UsageTracker()

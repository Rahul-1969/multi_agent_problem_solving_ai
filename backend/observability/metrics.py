import sqlite3
import datetime
import os
import threading
from config.path_config import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = os.path.join(DATA_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
METRICS_DB = os.path.join(CACHE_DIR, "metrics.db")

class Metrics:
    def __init__(self, db_path=METRICS_DB):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Table for AI provider calls
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ai_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        provider TEXT,
                        tier TEXT,
                        latency_ms REAL,
                        tokens_used INTEGER,
                        cached BOOLEAN
                    )
                """)
                # Table for classifiers
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS classifier (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        method TEXT,
                        intent TEXT
                    )
                """)
                # Table for fallbacks
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS fallback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        reason TEXT
                    )
                """)
                conn.commit()

    def _now(self):
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def record_gemini_call(self, tier: str, latency_ms: float, tokens: int | None, cached: bool = False):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO ai_calls (timestamp, provider, tier, latency_ms, tokens_used, cached)
                    VALUES (?, 'gemini', ?, ?, ?, ?)
                """, (self._now(), tier, latency_ms, tokens, cached))
                conn.commit()

    def record_classifier(self, method: str, intent: str):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO classifier (timestamp, method, intent)
                    VALUES (?, ?, ?)
                """, (self._now(), method, intent))
                conn.commit()

    def record_fallback(self, reason: str):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO fallback (timestamp, reason)
                    VALUES (?, ?)
                """, (self._now(), reason))
                conn.commit()

    def get_summary(self) -> dict:
        summary = {}
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                
                # Gemini Calls Today
                cur.execute("SELECT tier, COUNT(*) FROM ai_calls WHERE timestamp LIKE ? AND cached = 0 GROUP BY tier", (f"{today}%",))
                for row in cur.fetchall():
                    summary[f"{row[0]}_calls_today"] = row[1]
                
                # Cache Hits Today
                cur.execute("SELECT COUNT(*) FROM ai_calls WHERE timestamp LIKE ? AND cached = 1", (f"{today}%",))
                cache_hits = cur.fetchone()[0]
                summary["cache_hits_today"] = cache_hits
                
                # Average Latency
                cur.execute("SELECT AVG(latency_ms) FROM ai_calls WHERE cached = 0")
                row = cur.fetchone()
                summary["avg_latency_ms"] = round(row[0], 2) if row[0] else 0.0
                
                # Classifier stats
                cur.execute("SELECT method, COUNT(*) FROM classifier GROUP BY method")
                summary["classifier"] = {row[0]: row[1] for row in cur.fetchall()}
                
                # Fallbacks
                cur.execute("SELECT COUNT(*) FROM fallback")
                summary["fallback_count"] = cur.fetchone()[0]

        return summary

metrics = Metrics()

import threading
import time
import uuid
from typing import Final

from tools.pdf_store import PDFStore

DEFAULT_SESSION_ID: Final[str] = "default"
DEFAULT_SESSION_MAX_AGE_SECONDS: Final[int] = 60 * 60
DEFAULT_SESSION_CLEANUP_INTERVAL_SECONDS: Final[int] = 60 * 10


class PDFSession:
    """Wrapper that holds a PDFStore and the last access timestamp."""

    def __init__(self, store: PDFStore) -> None:
        self.store = store
        self.last_accessed = time.monotonic()

    def touch(self) -> None:
        self.last_accessed = time.monotonic()


class PDFSessionManager:
    """Manages multiple PDF sessions and keeps them isolated by session ID."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, PDFSession] = {}
        self._last_cleanup = time.monotonic()
        self._cleanup_interval_seconds = DEFAULT_SESSION_CLEANUP_INTERVAL_SECONDS
        self._max_age_seconds = DEFAULT_SESSION_MAX_AGE_SECONDS

    def create_session_id(self) -> str:
        """Return a new unique session ID."""
        return str(uuid.uuid4())

    def _normalize_session_id(self, session_id: str | None) -> str:
        if session_id and session_id.strip():
            return session_id.strip()
        return DEFAULT_SESSION_ID

    def _cleanup_if_needed(self) -> None:
        now = time.monotonic()
        if now - self._last_cleanup >= self._cleanup_interval_seconds:
            self._cleanup_sessions_locked(now, self._max_age_seconds)
            self._last_cleanup = now

    def _cleanup_sessions_locked(self, now: float, max_age_seconds: int) -> None:
        stale_sessions = [
            sid
            for sid, session in self._sessions.items()
            if now - session.last_accessed >= max_age_seconds
        ]
        for session_id in stale_sessions:
            self._sessions.pop(session_id, None)

    def cleanup_stale_sessions(self, max_age_seconds: int | None = None) -> None:
        """Remove sessions that have not been accessed within the configured timeout."""
        max_age_seconds = max_age_seconds or self._max_age_seconds
        with self._lock:
            self._cleanup_sessions_locked(time.monotonic(), max_age_seconds)

    def get_store(self, session_id: str | None) -> PDFStore:
        """Return the PDFStore for a session, creating it if necessary."""
        normalized_id = self._normalize_session_id(session_id)
        with self._lock:
            self._cleanup_if_needed()
            if normalized_id not in self._sessions:
                self._sessions[normalized_id] = PDFSession(PDFStore())
            session = self._sessions[normalized_id]
            session.touch()
            return session.store

    def load(self, session_id: str, pdf_path: str):
        store = self.get_store(session_id)
        return store.load(pdf_path)

    def clear(self, session_id: str) -> None:
        store = self.get_store(session_id)
        store.clear()

    def is_loaded(self, session_id: str | None) -> bool:
        store = self.get_store(session_id)
        return store.is_loaded()

    def status(self, session_id: str | None) -> dict:
        store = self.get_store(session_id)
        loaded = store.is_loaded()
        return {
            "loaded": loaded,
            "session_id": self._normalize_session_id(session_id),
            "filename": store.filename if loaded else None,
            "pages": store.page_count if loaded else None,
            "chunks": store.chunk_count if loaded else None,
        }

    def remove_session(self, session_id: str) -> None:
        normalized_id = self._normalize_session_id(session_id)
        with self._lock:
            self._sessions.pop(normalized_id, None)


pdf_session_manager = PDFSessionManager()

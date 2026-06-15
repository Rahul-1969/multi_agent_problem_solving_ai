"""
tools/pdf_store.py
In-memory session store for the currently loaded PDF.

Holds the parsed chunks so they don't get re-extracted on every question.
One PDF active at a time — loading a new PDF replaces the old one.

Usage:
    from tools.pdf_store import pdf_store
    pdf_store.load("path/to/file.pdf")
    chunks = pdf_store.chunks
    name   = pdf_store.filename
    loaded = pdf_store.is_loaded()
"""

from utils.logger import get_logger
import threading
from pathlib import Path
from typing import Final, TypedDict
from tools.pdf_reader import extract_pages, chunk_pages

logger = get_logger(__name__)


class PDFLoadInfo(TypedDict):
    """Metadata returned after successfully loading and chunking a PDF."""

    filename: str
    pages: int
    chunks: int


class PDFStore:
    """
    Stores the currently loaded PDF and its parsed chunks.

    Only one PDF is active at a time.
    Loading another PDF replaces the previous session.

    The lock protects concurrent FastAPI requests from mutating PDFStore state
    while another request is loading or clearing the active PDF.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._chunks: list[dict] = []
        self._filename: str = ""
        self._pages: int = 0

    def load(self, pdf_path: str) -> PDFLoadInfo:
        """
        Load and parse a PDF. Replaces any previously loaded PDF.
        Returns a summary dict: {filename, pages, chunks}
        """
        try:
            pages = extract_pages(pdf_path)
            chunks = chunk_pages(pages)

            # Compute first, then assign (avoid partial state)
            with self._lock:
                self._chunks = chunks
                self._filename = Path(pdf_path).name
                self._pages = len(pages)

            logger.info("PDF loaded: %s  |  %d pages  |  %d chunks",
                        self._filename, self._pages, len(self._chunks))

            return {
                "filename": self._filename,
                "pages":    self._pages,
                "chunks":   len(self._chunks),
            }
        except Exception:
            logger.exception("Failed to load PDF")
            self.clear()
            raise

    def clear(self) -> None:
        """Unload the current PDF."""
        with self._lock:
            logger.info("PDF unloaded: %s", self._filename)
            self._chunks = []
            self._filename = ""
            self._pages = 0

    def is_loaded(self) -> bool:
        with self._lock:
            return bool(self._chunks)

    @property
    def chunks(self) -> list[dict]:
        with self._lock:
            return list(self._chunks)

    @property
    def filename(self) -> str:
        with self._lock:
            return self._filename

    @property
    def page_count(self) -> int:
        with self._lock:
            return self._pages

    @property
    def chunk_count(self) -> int:
        with self._lock:
            return len(self._chunks)


# Global singleton — imported everywhere
pdf_store = PDFStore()
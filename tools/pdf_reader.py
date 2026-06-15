"""
tools/pdf_reader.py
Extracts text from a PDF with page-level granularity.

Returns a list of chunks, each with:
  - page_num   : page number (1-indexed)
  - text       : cleaned text of that page
  - char_count : number of characters

Also provides a helper to split pages into smaller overlapping chunks
for better context matching when pages are very long.
"""

from pathlib import Path
import re
from utils.logger import get_logger
import pdfplumber
from typing import Final, TypedDict

logger = get_logger(__name__)

# Max characters per chunk — keeps context within LLM token limits
CHUNK_SIZE: Final[int] = 800
CHUNK_OVERLAP: Final[int] = 150  # overlap so answers don't get cut at chunk boundaries
STEP_SIZE: Final[int] = CHUNK_SIZE - CHUNK_OVERLAP

_MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")


class PageData(TypedDict):
    page_num: int
    text: str
    char_count: int


class ChunkData(TypedDict):
    chunk_id: int
    page_num: int
    text: str
    _text_lower: str


def extract_pages(pdf_path: str | Path) -> list[PageData]:
    """
    Extract text from every page of a PDF.
    Returns list of dicts: {page_num, text, char_count}
    Raises FileNotFoundError or ValueError on bad input.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("File must be a .pdf")

    pages: list[PageData] = []
    try:
        with pdfplumber.open(path) as pdf:
            total = len(pdf.pages)
            logger.info("PDF has %d pages: %s", total, path.name)

            for i, page in enumerate(pdf.pages, start=1):
                raw = page.extract_text() or ""
                # Clean up extra whitespace
                text = _MULTI_NEWLINE_PATTERN.sub("\n\n", raw).strip()
                if text:
                    pages.append({
                        "page_num": i,
                        "text": text,
                        "char_count": len(text),
                    })
    except Exception:
        logger.exception("Failed to open or parse PDF: %s", path)
        raise

    logger.info("Extracted %d non-empty pages", len(pages))
    return pages


def chunk_pages(pages: list[PageData]) -> list[ChunkData]:
    """
    Split pages into overlapping chunks for better retrieval.
    Each chunk carries its source page_num for reference display.

    Returns list of dicts: {chunk_id, page_num, text}
    """
    chunks: list[ChunkData] = []
    cid = 0
    for page in pages:
        text = page["text"]
        text_len = len(text)
        pnum = page["page_num"]

        if text_len <= CHUNK_SIZE:
            chunks.append({
                "chunk_id": cid,
                "page_num": pnum,
                "text": text,
                "_text_lower": text.lower(),
            })
            cid += 1
        else:
            start = 0
            while start < text_len:
                end = start + CHUNK_SIZE
                chunk = text[start:end]
                chunks.append({
                    "chunk_id": cid,
                    "page_num": pnum,
                    "text": chunk,
                    "_text_lower": chunk.lower(),
                })
                cid += 1
                start += STEP_SIZE

    logger.info("Created %d chunks from %d pages", len(chunks), len(pages))
    return chunks
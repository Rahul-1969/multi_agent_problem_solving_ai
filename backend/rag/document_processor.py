"""
document_processor.py

Extracts clean text from uploaded documents (PDF, DOCX, TXT) and splits
it into overlapping chunks suitable for embedding. No LLM calls here —
pure text processing so it stays fast and testable in isolation.
"""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal

logger = logging.getLogger(__name__)

DocType = Literal[
    "syllabus", "placement", "college_faq", "resume",
    "scholarship", "interview_notes", "general",
]

# Tuned for academic PDFs: long enough to hold a full concept/paragraph,
# short enough to keep retrieval precise. Overlap prevents cutting a
# definition in half at a chunk boundary.
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50


@dataclass
class Chunk:
    """A single retrievable unit of text plus its provenance."""
    id: str
    text: str
    doc_id: str
    doc_name: str
    doc_type: DocType
    chunk_index: int
    metadata: dict = field(default_factory=dict)


class UnsupportedFileTypeError(ValueError):
    pass


def extract_text(file_path: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(file_path)
    if suffix == ".docx":
        return _extract_docx(file_path)
    if suffix in (".txt", ".md"):
        return _extract_txt(file_path)

    raise UnsupportedFileTypeError(
        f"Unsupported file type '{suffix}'. Supported: .pdf, .docx, .txt, .md"
    )


def _extract_pdf(file_path: str) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
        else:
            logger.warning("Page %d of %s produced no text (likely scanned image)", i, file_path)
    return "\n\n".join(pages)


def _extract_docx(file_path: str) -> str:
    import docx

    document = docx.Document(file_path)
    parts = [p.text for p in document.paragraphs if p.text.strip()]

    # Tables often hold placement data / eligibility criteria — don't drop them
    for table in document.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))

    return "\n\n".join(parts)


def _extract_txt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def clean_text(raw: str) -> str:
    """Normalize whitespace and strip common PDF extraction artifacts."""
    text = raw.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Recursive-ish splitter: prefer breaking on paragraph, then sentence,
    then hard word-boundary, so chunks stay semantically coherent instead
    of cutting mid-sentence.
    """
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(para) <= chunk_size:
            current = para
        else:
            # Paragraph itself is too long — split on sentences
            sentences = re.split(r"(?<=[.!?])\s+", para)
            current = ""
            for sentence in sentences:
                cand = f"{current} {sentence}".strip() if current else sentence
                if len(cand) <= chunk_size:
                    current = cand
                else:
                    if current:
                        chunks.append(current)
                    current = sentence[:chunk_size]  # hard cut as last resort

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            tail = chunks[i - 1][-overlap:]
            overlapped.append(f"{tail} {chunks[i]}".strip())
        chunks = overlapped

    return chunks


def process_document(
    file_path: str,
    doc_name: str,
    doc_type: DocType = "general",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Chunk]:
    """Full pipeline: extract -> clean -> chunk -> wrap in Chunk objects."""
    raw = extract_text(file_path)
    cleaned = clean_text(raw)

    if not cleaned:
        logger.warning("No extractable text found in %s", doc_name)
        return []

    doc_id = str(uuid.uuid4())
    pieces = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)

    return [
        Chunk(
            id=f"{doc_id}_{i}",
            text=piece,
            doc_id=doc_id,
            doc_name=doc_name,
            doc_type=doc_type,
            chunk_index=i,
        )
        for i, piece in enumerate(pieces)
    ]
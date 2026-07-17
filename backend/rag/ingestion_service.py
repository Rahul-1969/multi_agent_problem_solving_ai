"""
ingestion_service.py

Orchestrates the full upload -> text -> chunks -> embeddings -> store flow.
This is the single entry point the /knowledge/upload route should call —
routers should never touch document_processor or vector_store directly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from .document_processor import DocType, process_document
from .vector_store import VectorStore, get_vector_store

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    doc_id: str
    doc_name: str
    doc_type: DocType
    chunks_stored: int
    success: bool
    error: str | None = None


class IngestionService:
    def __init__(self, vector_store: VectorStore | None = None):
        self.vector_store = vector_store or get_vector_store()

    def ingest(
        self,
        user_id: str,
        file_path: str,
        doc_name: str,
        doc_type: DocType = "general",
    ) -> IngestionResult:
        try:
            chunks = process_document(file_path, doc_name=doc_name, doc_type=doc_type)

            if not chunks:
                return IngestionResult(
                    doc_id="",
                    doc_name=doc_name,
                    doc_type=doc_type,
                    chunks_stored=0,
                    success=False,
                    error="No extractable text found in document (may be a scanned image PDF).",
                )

            stored = self.vector_store.add_chunks(user_id, chunks)
            return IngestionResult(
                doc_id=chunks[0].doc_id,
                doc_name=doc_name,
                doc_type=doc_type,
                chunks_stored=stored,
                success=True,
            )

        except Exception as exc:
            logger.exception("Ingestion failed for %s (user=%s)", doc_name, user_id)
            return IngestionResult(
                doc_id="",
                doc_name=doc_name,
                doc_type=doc_type,
                chunks_stored=0,
                success=False,
                error=str(exc),
            )

    def list_documents(self, user_id: str) -> List[dict]:
        return self.vector_store.list_documents(user_id)

    def delete_document(self, user_id: str, doc_id: str) -> None:
        self.vector_store.delete_document(user_id, doc_id)


_service_instance: IngestionService | None = None


def get_ingestion_service() -> IngestionService:
    global _service_instance
    if _service_instance is None:
        _service_instance = IngestionService()
    return _service_instance
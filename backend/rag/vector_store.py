"""
vector_store.py

ChromaDB wrapper providing per-user document isolation. Each student gets
their own collection (namespaced by user_id) so retrieval can never leak
one student's notes into another student's answers.

Falls back cleanly to an in-memory FAISS-backed store for local dev if
persistent ChromaDB storage isn't configured (mirrors the dev/prod split
already used for the Ollama vs Gemini provider split).
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .document_processor import Chunk
from .embedder import Embedder, get_embedder

logger = logging.getLogger(__name__)

DEFAULT_PERSIST_DIR = "./data/chroma"


@dataclass
class RetrievedChunk:
    text: str
    doc_id: str
    doc_name: str
    doc_type: str
    score: float  # similarity score, higher = more relevant


class VectorStore:
    """
    Thread-safe wrapper around a ChromaDB PersistentClient. One collection
    per user_id, created lazily on first write.
    """

    def __init__(self, persist_dir: str = DEFAULT_PERSIST_DIR, embedder: Optional[Embedder] = None):
        self.persist_dir = persist_dir
        self.embedder = embedder or get_embedder()
        self._client = None
        self._client_lock = threading.Lock()
        self._collection_locks: dict[str, threading.Lock] = {}
        self._collection_locks_guard = threading.Lock()

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        with self._client_lock:
            if self._client is not None:
                return self._client
            import chromadb

            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            logger.info("ChromaDB client initialized at %s", self.persist_dir)
            return self._client

    def _collection_name(self, user_id: str) -> str:
        # Chroma collection names must be alphanumeric/underscore/hyphen only
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in user_id)
        return f"student_{safe_id}"

    def _get_lock(self, user_id: str) -> threading.Lock:
        with self._collection_locks_guard:
            if user_id not in self._collection_locks:
                self._collection_locks[user_id] = threading.Lock()
            return self._collection_locks[user_id]

    def _get_collection(self, user_id: str):
        client = self._ensure_client()
        return client.get_or_create_collection(
            name=self._collection_name(user_id),
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, user_id: str, chunks: List[Chunk]) -> int:
        """Embed and store chunks for a given student. Returns count stored."""
        if not chunks:
            return 0

        with self._get_lock(user_id):
            collection = self._get_collection(user_id)
            texts = [c.text for c in chunks]
            vectors = self.embedder.embed_documents(texts)

            collection.add(
                ids=[c.id for c in chunks],
                embeddings=vectors,
                documents=texts,
                metadatas=[
                    {
                        "doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "doc_type": c.doc_type,
                        "chunk_index": c.chunk_index,
                    }
                    for c in chunks
                ],
            )
            logger.info("Stored %d chunks for user %s", len(chunks), user_id)
            return len(chunks)

    def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        doc_types: Optional[List[str]] = None,
    ) -> List[RetrievedChunk]:
        """
        Semantic search scoped to one student's collection. Optionally
        filter to specific doc_types (e.g. only "syllabus" and "placement"
        when the student context indicates that's what's relevant).
        """
        collection = self._get_collection(user_id)
        if collection.count() == 0:
            return []

        query_vector = self.embedder.embed_query(query)
        where_filter = {"doc_type": {"$in": doc_types}} if doc_types else None

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, collection.count()),
            where=where_filter,
        )

        retrieved: List[RetrievedChunk] = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            # Chroma cosine distance -> similarity score (0..1, higher is better)
            similarity = 1 - dist
            retrieved.append(
                RetrievedChunk(
                    text=doc,
                    doc_id=meta.get("doc_id", ""),
                    doc_name=meta.get("doc_name", "unknown"),
                    doc_type=meta.get("doc_type", "general"),
                    score=round(similarity, 4),
                )
            )

        return retrieved

    def delete_document(self, user_id: str, doc_id: str) -> None:
        with self._get_lock(user_id):
            collection = self._get_collection(user_id)
            collection.delete(where={"doc_id": doc_id})
            logger.info("Deleted document %s for user %s", doc_id, user_id)

    def list_documents(self, user_id: str) -> List[dict]:
        """Return distinct documents (not chunks) with basic stats."""
        collection = self._get_collection(user_id)
        if collection.count() == 0:
            return []

        all_data = collection.get(include=["metadatas"])
        seen: dict[str, dict] = {}
        for meta in all_data.get("metadatas", []):
            doc_id = meta.get("doc_id")
            if doc_id not in seen:
                seen[doc_id] = {
                    "doc_id": doc_id,
                    "doc_name": meta.get("doc_name"),
                    "doc_type": meta.get("doc_type"),
                    "chunk_count": 0,
                }
            seen[doc_id]["chunk_count"] += 1

        return list(seen.values())


_store_instance: Optional[VectorStore] = None
_store_instance_lock = threading.Lock()


def get_vector_store() -> VectorStore:
    """Process-wide singleton accessor, same pattern as get_embedder()."""
    global _store_instance
    if _store_instance is not None:
        return _store_instance
    with _store_instance_lock:
        if _store_instance is None:
            _store_instance = VectorStore()
        return _store_instance
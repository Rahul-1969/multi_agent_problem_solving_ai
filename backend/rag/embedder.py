"""
embedder.py

Wraps a sentence-transformers embedding model behind a small, swappable
interface so the rest of the RAG pipeline never touches the model directly.
Mirrors the ProviderFactory pattern used elsewhere in the codebase: one
factory function, one lazily-loaded singleton, easy to mock in tests.
"""

from __future__ import annotations

import logging
import threading
from functools import lru_cache
from typing import List

logger = logging.getLogger(__name__)

# BGE-small is a strong, cheap default: 384-dim, fast on CPU, good recall
# for short academic passages. Swap via EMBEDDING_MODEL_NAME if needed.
DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384


class Embedder:
    """
    Thin wrapper around a SentenceTransformer model.

    Thread-safe lazy loading: the underlying model is loaded once, on first
    use, guarded by a lock (same defensive pattern as provider_factory's
    thread-safety fix).
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self._model = None
        self._load_lock = threading.Lock()

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:  # double-checked locking
                return
            logger.info("Loading embedding model: %s", self.model_name)
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded: %s", self.model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of chunks for storage. Adds BGE's recommended
        passage prefix so retrieval quality matches the model's training."""
        if not texts:
            return []
        self._ensure_loaded()
        prefixed = [f"passage: {t}" for t in texts]
        vectors = self._model.encode(
            prefixed,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single user query for search. BGE expects a distinct
        'query:' prefix from the one used for stored passages."""
        self._ensure_loaded()
        vector = self._model.encode(
            f"query: {text}",
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return vector.tolist()


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    """Process-wide singleton accessor, analogous to get_provider_factory()."""
    return Embedder()
"""
backend/rag/retriever.py

This module provides the Retriever class, which sits between vector_store.py 
(raw semantic search) and rag_pipeline.py (prompt assembly and LLM call). 
It wraps the raw VectorStore search to provide score thresholding, fallback 
retrieval logic, and formatting utilities to prepare retrieved context for the LLM.
"""

import threading
import logging
from typing import List, Optional

from backend.rag.vector_store import RetrievedChunk, get_vector_store

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, min_score: float = 0.35) -> None:
        """
        Initialize the retriever with a minimum similarity score threshold.
        Low-scoring chunks are noise and are dropped before being passed to the LLM.
        """
        self.min_score = min_score
        self._vector_store = get_vector_store()
        
    def retrieve(
        self, 
        user_id: str, 
        query: str, 
        top_k: int = 5, 
        doc_types: Optional[List[str]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks from the vector store for a given query, 
        filtered by the minimum score threshold, and sorted by score descending.
        """
        raw_results = self._vector_store.search(
            user_id=user_id,
            query=query,
            top_k=top_k,
            doc_types=doc_types
        )
        
        # Filter out chunks below the threshold
        filtered_chunks = [chunk for chunk in raw_results if chunk.score >= self.min_score]
        
        # Sort by score descending (highest similarity first)
        filtered_chunks.sort(key=lambda chunk: chunk.score, reverse=True)
        
        return filtered_chunks

    def retrieve_with_fallback(
        self, 
        user_id: str, 
        query: str, 
        top_k: int = 5, 
        doc_types: Optional[List[str]] = None
    ) -> List[RetrievedChunk]:
        """
        Attempt to retrieve chunks filtered by doc_types. If no chunks meet 
        the threshold, retry the query across all doc_types before giving up.
        """
        results = self.retrieve(user_id, query, top_k, doc_types)
        
        if not results and doc_types:
            logger.warning(
                "No results found for user %s with doc_types %s. Falling back to search without doc_types.",
                user_id, doc_types
            )
            # Retry without the doc_types filter
            results = self.retrieve(user_id, query, top_k, doc_types=None)
            
        return results

    @staticmethod
    def format_for_prompt(chunks: List[RetrievedChunk]) -> str:
        """
        Format retrieved chunks into a clean context block for injection into an LLM prompt.
        """
        if not chunks:
            return ""
            
        formatted_chunks = []
        for chunk in chunks:
            formatted_chunks.append(f"[Source: {chunk.doc_name}]\n{chunk.text.strip()}")
            
        return "\n\n".join(formatted_chunks)

    @staticmethod
    def format_for_llm_context(chunks: List[RetrievedChunk]) -> str:
        """
        Format retrieved chunks for LLM prompt injection, WITHOUT source labels,
        so the LLM treats the context as one unified knowledge base rather than
        distinct labeled documents (labeling was causing the LLM to echo "Source:"
        into its own generated answers). Source attribution to the user is handled
        separately via the pipeline's `sources` metadata field, not via prompt text.
        """
        if not chunks:
            return ""
            
        formatted_chunks = []
        for chunk in chunks:
            formatted_chunks.append(chunk.text.strip())
            
        return "\n\n---\n\n".join(formatted_chunks)


# Lazy singleton pattern for the Retriever
_retriever_instance: Optional[Retriever] = None
_lock = threading.Lock()

def get_retriever() -> Retriever:
    """
    Returns the singleton instance of the Retriever.
    """
    global _retriever_instance
    if _retriever_instance is None:
        with _lock:
            if _retriever_instance is None:
                _retriever_instance = Retriever()
    return _retriever_instance

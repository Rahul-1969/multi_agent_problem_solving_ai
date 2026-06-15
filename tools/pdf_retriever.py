"""
tools/pdf_retriever.py
Retrieves the most relevant chunks from a parsed PDF for a given query.

Strategy — lightweight TF-IDF style scoring (no heavy ML models needed):
  1. Tokenise query into keywords (remove stopwords)
  2. Score each chunk by:
       keyword_hits   (how many query words appear in chunk)
     + exact_phrase   (bonus if full query phrase appears verbatim)
     + density        (keyword_hits / chunk_word_count for short-chunk bias)
  3. Return top-N chunks, sorted by score, deduplicated by page

No external ML libraries needed — runs instantly even on i3/8GB RAM.
"""

import re
from utils.logger import get_logger
import heapq
from collections import Counter
from operator import itemgetter
from typing import Final

logger = get_logger(__name__)

# Common English stopwords — excluded from keyword matching (immutable)
_STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "can", "could", "should", "may", "might", "shall",
    "in", "on", "at", "by", "for", "with", "about", "against",
    "between", "through", "of", "to", "from", "up", "down",
    "and", "or", "but", "not", "so", "yet",
    "i", "me", "my", "we", "our", "you", "your",
    "it", "its", "this", "that", "these", "those",
    "what", "which", "who", "how", "when", "where", "why",
    "tell", "explain", "define", "describe", "give", "list",
    "me", "please",
})

# Precompiled token regex for performance
_TOKEN_PATTERN = re.compile(r"\b[a-z]{2,}\b")

# Scoring constants
PHRASE_BONUS: Final[int] = 3
DENSITY_MULTIPLIER: Final[int] = 10


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, remove stopwords."""
    tokens = _TOKEN_PATTERN.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


def retrieve_chunks(
    query: str,
    chunks: list[dict],
    top_n: int = 4,
) -> list[dict]:
    """
    Score and return the top_n most relevant chunks for the query.

    Each returned dict has:
      chunk_id, page_num, text, score
    """
    if not chunks:
        return []

    q_tokens = _tokenize(query)
    q_lower = query.lower()
    q_phrase = q_lower.strip()
    if not q_tokens:
        return []
    q_counter = Counter(q_tokens)

    scored: list[dict] = []
    for chunk in chunks:
        # Try to reuse cached lower-text and token counters
        c_text = chunk.get("_text_lower")
        if c_text is None:
            c_text = chunk["text"].lower()
            tokens = _tokenize(c_text)
            c_counter = Counter(tokens)
            token_count = len(tokens)
            # Cache for future queries
            chunk["_text_lower"] = c_text
            chunk["_token_counter"] = c_counter
            chunk["_token_count"] = token_count
        else:
            c_counter = chunk.get("_token_counter")
            token_count = chunk.get("_token_count", 0)

        # Keyword hit score (weighted by query term frequency).
        # Iterate over q_counter.items() because query counters are small,
        # and this avoids constructing a temporary Counter object.
        kw_score = sum(
            min(c_counter.get(tok, 0), freq)
            for tok, freq in q_counter.items()
        )

        # Exact phrase bonus
        phrase_bonus = PHRASE_BONUS if q_phrase in c_text else 0

        # Density: avoid very long chunks dominating just by size
        density = kw_score / max(token_count, 1) * DENSITY_MULTIPLIER

        total = kw_score + phrase_bonus + density

        if total > 0:
            scored.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "page_num": chunk["page_num"],
                    "text": chunk["text"],
                    "score": round(total, 3),
                }
            )

    # Select top candidates using a heap (more efficient than sorting the whole list)
    if scored:
        k = min(len(scored), max(top_n * 5, top_n))
        scored = heapq.nlargest(k, scored, key=itemgetter("score"))

    # Deduplicate: keep only best chunk per page
    seen_pages: set[int] = set()
    results: list[dict] = []
    for item in scored:
        if item["page_num"] not in seen_pages:
            results.append(item)
            seen_pages.add(item["page_num"])
        if len(results) >= top_n:
            break

    logger.debug("Retrieved %d chunks for query: %s", len(results), query[:50])
    return results
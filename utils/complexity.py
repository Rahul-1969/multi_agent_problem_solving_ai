"""
utils/complexity.py
Detects query complexity for agent pipeline selection.

Fix: Removed bare "write", "generate", "create" from _HIGH_KEYWORDS.
These were too broad — "create table in mysql", "generate pdf",
"create react app" were all returning high complexity incorrectly.
Kept specific phrases: "write a", "create a", "generate code".
"""

from utils.logger import get_logger
logger = get_logger(__name__)

# ─── High complexity — code generation, implementation, analysis ──────────────
_HIGH_KEYWORDS = {
    # Specific code-gen phrases (NOT bare "write" or "create")
    "write a", "write the", "write an",
    "program for", "program to",
    "code for", "code to",
    "implement", "implementation",
    "build a", "build an",
    "create a", "create an",        # kept with article — avoids "create table"
    "develop a", "design a", "design an",
    "generate code", "generate a program",  # specific, not bare "generate"

    # Analysis / problem solving
    "optimize", "optimise", "analyse", "analyze",
    "debug", "fix the", "fix this", "solve",
    "algorithm for", "algorithm to",
    "proof", "derive",
    "time complexity", "space complexity",
    "complexity of",
}

# ─── Medium complexity — explanations, comparisons ───────────────────────────
_MEDIUM_KEYWORDS = {
    "explain", "how does", "how do", "how to",
    "describe", "example of", "examples of",
    "difference between", "compare", " vs ", "versus",
    "working of", "use of", "uses of",
    "advantages", "disadvantages", "pros", "cons",
    "features of", "applications of",
    "why is", "why does", "why do", "architecture",
    "working", "flow", "steps", "principle",
    "mechanism", "calculate",
}

# ─── Low complexity — definitions, facts ─────────────────────────────────────
_LOW_KEYWORDS = {
    "what is", "what are", "what was",
    "define", "definition",
    "meaning of", "who is", "who was",
    "when was", "where is", "where was",
    "how many", "how much",
    "what does", "full form", "abbreviation",
    "list of", "types of", "name the",
    "give me", "tell me",
}


def detect_complexity(query: str) -> str:
    """
    Returns 'low', 'medium', or 'high'.
    Pure rule-based — no LLM calls, no latency.
    """
    q = query.lower().strip()

    if any(kw in q for kw in _HIGH_KEYWORDS):
        logger.debug("Complexity: high (keyword match)")
        return "high"

    if any(kw in q for kw in _MEDIUM_KEYWORDS):
        logger.debug("Complexity: medium (keyword match)")
        return "medium"

    if any(kw in q for kw in _LOW_KEYWORDS):
        logger.debug("Complexity: low (keyword match)")
        return "low"

    # Word-count heuristic — no LLM fallback
    word_count = len(q.split())
    if word_count <= 6:
        return "low"
    if word_count <= 15:
        return "medium"
    return "high"

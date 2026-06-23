"""
pipelines/general_pipeline.py
Handles general knowledge queries — facts, trivia, current events, opinions.

Returns PipelineResult instead of plain strings to enable
structured data flow through the formatter layer.

General domain is STRICTLY for:
- Current facts  : "What is the capital of India"
- Current events : "How many runs has Virat scored", "election results"
- Trivia          : "Who invented the telephone"
- Conversational  : "Hi", "Thanks"
- Anything not covered by other domains

NOT for CS concepts (→ education), coding (→ coding), medical (→ medical),
or college (→ college).

Uses compiled regex patterns for efficient matching.
"""

from utils.logger import get_logger
import re
from llm.ollama_client  import call_llm
from utils.complexity   import detect_complexity
from utils.text_cleaner import clean_text
from pipelines.pipeline_result import PipelineResult
from backend.models.response_models import GeneralData

logger = get_logger(__name__)

_GENERAL_SYSTEM = (
    "Answer directly and concisely.\n"
    "No preamble.\n"
    "Lead with the answer.\n"
    "If uncertain, say so.\n"
    "Do not invent facts.\n"
    "Plain English.\n"
    "Short sentences.\n"
)

_EXPLANATORY_SYSTEM = (
    "Provide a detailed and structured explanation suitable for B.Tech and university exams.\n"
    "Include ALL of the following sections:\n"
    "1. Definition\n"
    "2. Explanation\n"
    "3. Working or Principles\n"
    "4. Key Points\n"
    "5. Advantages and Disadvantages (if applicable)\n"
    "6. Applications\n"
    "7. Example\n"
    "8. Summary\n"
    "Use headings and bullet points.\n"
    "Write long, thorough answers. Do not skip any section.\n"
)

# ── Compiled patterns (built once at import time) ─────────────────────────────
_FACTUAL_RE = re.compile(
    r"^(what is|what are|what was|who is|who was|when was|where is|"
    r"how many|how much|which|name the|list|tell me about|give me|"
    r"define|what's|who's|when did|where did|how did|capital of|"
    r"president of|prime minister of|currency of|population of)\b",
    re.IGNORECASE,
)

_CURRENT_EVENTS_RE = re.compile(
    r"\b(latest|current|recent|today|yesterday|this year|last year|"
    r"right now|as of|score|scored|election|result|winner|match|"
    r"tournament|championship|news|update|announcement)\b",
    re.IGNORECASE,
)

_CONVERSATIONAL_RE = re.compile(
    r"^(hi|hello|hey|thanks|thank you|good morning|good evening|"
    r"good night|bye|goodbye|how are you|what's up|sup)\b",
    re.IGNORECASE,
)

_EXPLANATORY_RE = re.compile(
    r"^(why|how does|how do|explain|describe|difference between|"
    r"compare|advantages|disadvantages|features|working of|"
    r"architecture of|importance of|applications of|uses of|benefits of)\b",
    re.IGNORECASE,
)

_TOKEN_CAP = {
    "conversational": 150,
    "factual": 400,
    "explanatory": 1200,
    "general": 800,
}

def _query_type(query: str) -> str:
    """Classify query into: conversational | factual | explanatory | general"""
    q = query.strip()
    if _CONVERSATIONAL_RE.match(q):
        return "conversational"
    if _FACTUAL_RE.match(q) or _CURRENT_EVENTS_RE.search(q):
        return "factual"
    if _EXPLANATORY_RE.match(q):
        return "explanatory"
    return "general"


def _call_safe(prompt: str, tokens: int, system: str) -> str:
    """Wrapper around call_llm with error handling."""
    try:
        raw = call_llm(prompt=prompt, system=system, num_predict=tokens)
        return clean_text(raw)
    except RuntimeError as exc:
        logger.error(
            "General pipeline LLM error: %s",
            exc
        )

        return (
            "⚠️ LLM unavailable.\n"
            f"Error: {exc}"
        )


def general_pipeline(query: str) -> PipelineResult:
    """
    Entry point for general queries.
    Returns structured general data alongside formatted display string.
    """
    qtype = _query_type(query)
    level = detect_complexity(query)
    logger.info("General pipeline: type=%s  complexity=%s", qtype, level)

    if qtype == "conversational":
        response = _call_safe(query, tokens=_TOKEN_CAP["conversational"], system=_GENERAL_SYSTEM)
        return PipelineResult(response=response, data=GeneralData(answer=response))

    if qtype == "factual":
        # Current events / factual — single direct call, concise answer
        response = _call_safe(query, tokens=_TOKEN_CAP["factual"], system=_GENERAL_SYSTEM)
        return PipelineResult(response=response, data=GeneralData(answer=response))

    if qtype == "explanatory":
        response = _call_safe(
            query,
            tokens=_TOKEN_CAP["explanatory"],
            system=_EXPLANATORY_SYSTEM,
        )
        return PipelineResult(response=response, data=GeneralData(answer=response))

    # General fallback
    response = _call_safe(query, tokens=_TOKEN_CAP["general"], system=_GENERAL_SYSTEM)
    return PipelineResult(response=response, data=GeneralData(answer=response))

"""
agents/llm_agents.py
Centralised implementation of LLM-driven agent behavior.

This module contains the core work for the base, refiner, and expert agents.
Individual legacy wrappers in base_agent.py, refiner_agent.py, and
expert_agent.py delegate to these implementations.
"""

from utils.logger import get_logger
from typing import Final

from agents.models import AgentResult
from llm.ollama_client import call_llm
from utils.text_cleaner import clean_text

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------
_SYSTEM_BASE: Final[str] = (
    "Answer directly and concisely. "
    "Lead with the answer immediately — no preamble, no 'Great question'. "
    "Use plain English. Short sentences. No repetition."
)
_TOKEN_ESTIMATE_FACTOR: Final[float] = 0.25  # ~1 token per 4 chars


def _estimate_tokens(text: str) -> int:
    return max(1, int(len(text) * _TOKEN_ESTIMATE_FACTOR))


def _estimate_confidence(text: str) -> float:
    length = len(text)
    if 100 <= length <= 300:
        return 0.95
    if length < 50:
        return 0.70
    if length > 500:
        return 0.75
    return 0.85


def run_base_agent(query: str) -> AgentResult:
    """
    Run the base agent and return an AgentResult.
    """
    response = call_llm(
        prompt=query,
        system=_SYSTEM_BASE,
        num_predict=250,
    )

    answer = clean_text(response)
    return AgentResult(
        answer=answer,
        confidence=_estimate_confidence(answer),
        tokens=_estimate_tokens(answer),
        should_refine=True,
        should_expert=False,
    )

# ---------------------------------------------------------------------------
# Refiner agent
# ---------------------------------------------------------------------------
_SYSTEM_REFINER: Final[str] = (
    "You are an editor.\n"
    "Remove filler words and repetition.\n"
    "Do NOT add information.\n"
    "Do NOT explain further.\n"
    "Do NOT expand.\n"
    "Keep all important facts.\n"
    "Output should be shorter than the input whenever possible.\n"
    "Return only the rewritten answer.\n"
    "Plain English.\n"
)


def run_refiner_agent(result: AgentResult) -> AgentResult:
    """
    Refine and compress a base agent result.
    """
    prompt = (
        "Tighten this answer. Remove filler. "
        "Keep all key information.\n\n"
        f"{result.answer}"
    )

    response = call_llm(
        prompt=prompt,
        system=_SYSTEM_REFINER,
        num_predict=180,
    )

    refined_answer = clean_text(response)
    tokens = _estimate_tokens(refined_answer)

    return AgentResult(
        answer=refined_answer,
        confidence=result.confidence,
        tokens=tokens,
        should_refine=False,
        should_expert=result.should_expert,
    )

# ---------------------------------------------------------------------------
# Expert agent
# ---------------------------------------------------------------------------
_SYSTEM_EXPERT: Final[str] = (
    "You are a senior engineer.\n"
    "Add exactly ONE missing insight, edge case, or gotcha.\n"
    "Do NOT repeat the original answer.\n"
    "Do NOT explain everything again.\n"
    "Do NOT add multiple insights.\n"
    "Return one short paragraph only.\n"
)


def run_expert_agent(result: AgentResult, query: str) -> AgentResult:
    """
    Add a single expert insight to an AgentResult.
    """
    prompt = (
        f"Query context: {query}\n\n"
        f"Here is an answer:\n\n{result.answer}\n\n"
        "Add exactly ONE important insight, edge case, or gotcha.\n"
        "Return one short paragraph only."
    )

    response = call_llm(
        prompt=prompt,
        system=_SYSTEM_EXPERT,
        num_predict=150,
    )

    insight = clean_text(response)
    enhanced_answer = f"{result.answer}\n\n**Expert Insight:**\n{insight}"
    tokens = _estimate_tokens(enhanced_answer)

    return AgentResult(
        answer=enhanced_answer,
        confidence=result.confidence,
        tokens=tokens,
        should_refine=False,
        should_expert=False,
    )

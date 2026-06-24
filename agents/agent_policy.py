"""
agents/agent_policy.py
Policy layer for adaptive agent execution.

Decides whether to run refiner/expert based on query complexity,
answer confidence, and other metadata. Reduces unnecessary LLM calls
for low-complexity queries and high-confidence answers.
"""

from utils.logger import get_logger
from typing import Final, Literal

from agents.models import AgentResult

logger = get_logger(__name__)

__all__ = ["should_run_refiner", "should_run_expert"]

# Decision thresholds
_MIN_CONFIDENCE_FOR_EXPERT: Final[float] = 0.6
_MIN_ANSWER_LENGTH_FOR_EXPERT: Final[int] = 50
_MAX_TOKENS_BEFORE_SKIP_EXPERT: Final[int] = 400

ComplexityLevel = Literal["low", "medium", "high"]


def should_run_refiner(result: AgentResult, complexity: ComplexityLevel) -> bool:
    """
    Decide whether to run the refiner agent.

    Rules:
    - low complexity: skip (base answer is good enough)
    - medium complexity: skip (base answer is sufficient; quality
      preserved through prompt engineering, not extra agents)
    - high complexity: always run (prepare for expert refinement)

    Args:
        result: AgentResult from base agent.
        complexity: Detected complexity level.

    Returns:
        True if refiner should run, False otherwise.
    """
    if complexity in ("low", "medium"):
        logger.debug("Skipping refiner: complexity=%s", complexity)
        return False

    # high: always refine
    logger.debug("Running refiner: complexity=%s", complexity)
    return True


def should_run_expert(result: AgentResult, complexity: ComplexityLevel) -> bool:
    """
    Decide whether to run the expert agent.

    Rules:
    - Skip if complexity is low or medium (base + refiner enough)
    - For high complexity: run only if
      * answer is substantial (> 50 chars)
      * confidence is low (< 0.6) — model uncertain
      * tokens are not excessive (< 400) — room to add insight

    Args:
        result: AgentResult from refiner (or base if refiner skipped).
        complexity: Detected complexity level.

    Returns:
        True if expert should run, False otherwise.
    """
    if complexity != "high":
        logger.debug("Skipping expert: complexity=%s (not high)", complexity)
        return False

    # High complexity: apply heuristics
    reasons_to_skip = []

    if len(result.answer) < _MIN_ANSWER_LENGTH_FOR_EXPERT:
        reasons_to_skip.append(f"answer too short ({len(result.answer)} chars)")

    if result.confidence >= _MIN_CONFIDENCE_FOR_EXPERT:
        reasons_to_skip.append(f"confidence too high ({result.confidence:.2f})")

    if result.tokens >= _MAX_TOKENS_BEFORE_SKIP_EXPERT:
        reasons_to_skip.append(f"tokens approaching limit ({result.tokens})")

    if reasons_to_skip:
        logger.debug("Skipping expert: %s", ", ".join(reasons_to_skip))
        return False

    logger.debug(
        "Running expert: complexity=high, confidence=%.2f, tokens=%d",
        result.confidence,
        result.tokens,
    )
    return True

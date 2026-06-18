"""
utils/agent_executor.py
Orchestrates the multi-agent pipeline with adaptive execution.

Architecture:
    Complexity Detection
            ↓
        Base Agent
            ↓
    Policy: should_run_refiner?
       ↙              ↘
    YES              NO
     ↓                ↓
  Refiner      [skip refinement]
     ↓                ↓
    [Policy: should_run_expert?]
       ↙              ↘
    YES              NO
     ↓                ↓
  Expert       [skip expert]
     ↓                ↓
    └────────┬────────┘
             ↓
         Final Answer

Execution patterns:
    low    → base (1 call, ~250 tokens)
    medium → base → refiner (2 calls, ~250 tokens)
    high   → base → refiner → expert? (2-3 calls, ~250-450 tokens)
"""

import time
from typing import Final, Literal

from agents.base_agent import base_agent
from agents.expert_agent import expert_enhance
from agents.models import AgentResult
from agents.refiner_agent import refine_answer
from agents.agent_policy import should_run_refiner, should_run_expert
from utils.cache import cached_response
from utils.complexity import detect_complexity
from utils.logger import get_logger

logger = get_logger(__name__)

__all__ = ["run_agents"]

_OLLAMA_ERROR_MESSAGE: Final[str] = (
    "⚠️  The AI model (Ollama) is currently unavailable.\n"
    "Make sure Ollama is running:\n"
    "    ollama serve\n"
    "    ollama pull phi3:mini\n"
)

ComplexityLevel = Literal["low", "medium", "high"]
_DEFAULT_LEVEL: Final[ComplexityLevel] = "medium"
_VALID_LEVELS: Final[frozenset[ComplexityLevel]] = frozenset({"low", "medium", "high"})


@cached_response(maxsize=128)
def _cached_base_result(query: str) -> AgentResult:
    """Cache base agent results for repeated queries."""
    logger.info("Running base agent (cached)")
    return base_agent(query)


def _run_base(query: str) -> AgentResult:
    """Run base agent."""
    logger.info("Running base agent")
    return base_agent(query)


def _run_refiner(result: AgentResult) -> AgentResult:
    """Run refiner agent, with graceful fallback."""
    logger.info("Running refiner agent")
    return refine_answer(result)


def _run_expert(result: AgentResult, query: str) -> AgentResult:
    """Run expert agent, with graceful fallback."""
    logger.info("Running expert agent")
    return expert_enhance(result, query)


def run_agents(query: str, complexity_override: ComplexityLevel | None = None) -> str:
    """
    Run the appropriate agent chain with adaptive execution.

    This is the main entry point. It maintains backward compatibility
    by returning a plain string (the final answer), while internally
    managing AgentResult objects through the pipeline.

    Args:
        query               : user query
        complexity_override : force a specific level ('low'/'medium'/'high')
                              used by domain pipelines to avoid re-detecting

    Returns:
        str: The final answer from the agent chain.

    Raises:
        Returns error message on failure (does not raise).
    """
    start_time = time.time()
    refiner_used = False
    expert_used = False

    try:
        # 1. Detect complexity
        level = complexity_override or detect_complexity(query)
        if level not in _VALID_LEVELS:
            logger.warning(
                "Unknown complexity '%s'. Defaulting to medium.",
                level
            )
            level = _DEFAULT_LEVEL

        logger.info("Agent executor started: complexity=%s", level)

        if level == "low":
            logger.info("Low complexity detected — using cached base result")
            try:
                base_result = _cached_base_result(query)
            except Exception:
                logger.exception("Base agent failed")
                return (
                    f"{_OLLAMA_ERROR_MESSAGE}\n"
                    "The base agent could not process your query."
                )

            elapsed = time.time() - start_time
            logger.info(
                (
                    "Agents | complexity=%s | tokens=%d | confidence=%.2f | "
                    "refiner=no | expert=no | elapsed=%.2fs"
                ),
                level,
                base_result.tokens,
                base_result.confidence,
                elapsed,
            )
            return base_result.answer

        # 2. Run base agent
        try:
            base_result = _run_base(query)
        except Exception:
            logger.exception("Base agent failed")
            return (
                f"{_OLLAMA_ERROR_MESSAGE}\n"
                "The base agent could not process your query."
            )

        # 3. Decide: run refiner?
        refiner_error = False
        if should_run_refiner(base_result, level):
            try:
                base_result = _run_refiner(base_result)
                refiner_used = True
            except Exception:
                logger.exception("Refiner failed")
                refiner_error = True

        # 4. Decide: run expert?
        expert_error = False
        if should_run_expert(base_result, level):
            try:
                base_result = _run_expert(base_result, query)
                expert_used = True
            except Exception:
                logger.exception("Expert failed")
                expert_error = True

        # 5. Extract final answer
        final_answer = base_result.answer
        if refiner_error:
            final_answer += "\n\n[Refiner step failed: the answer above may not be fully polished.]"
        if expert_error:
            final_answer += "\n\n[Expert step failed: the answer above may not include deep insights.]"

        # 6. Log execution statistics
        elapsed = time.time() - start_time
        logger.info(
            (
                "Agents | complexity=%s | tokens=%d | confidence=%.2f | "
                "refiner=%s | expert=%s | elapsed=%.2fs"
            ),
            level,
            base_result.tokens,
            base_result.confidence,
            "yes" if refiner_used else "no",
            "yes" if expert_used else "no",
            elapsed,
        )

        return final_answer

    except Exception as exc:
        logger.exception("Agent pipeline failed unexpectedly")
        return (
            f"{_OLLAMA_ERROR_MESSAGE}\n"
            f"Error: {exc}"
        )
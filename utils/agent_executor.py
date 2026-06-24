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

from agents.llm_agents import (
    run_base_agent,
    run_expert_agent,
    run_refiner_agent,
)
from agents.models import AgentResult
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
    return run_base_agent(query)


def _run_base(query: str) -> AgentResult:
    """Run base agent."""
    logger.info("Running base agent")
    return run_base_agent(query)


def _run_refiner(result: AgentResult) -> AgentResult:
    """Run refiner agent, with graceful fallback."""
    logger.info("Running refiner agent")
    return run_refiner_agent(result)


def _run_expert(result: AgentResult, query: str) -> AgentResult:
    """Run expert agent, with graceful fallback."""
    logger.info("Running expert agent")
    return run_expert_agent(result, query)


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
    pipeline_start = time.time()
    refiner_used = False
    expert_used = False
    base_elapsed = 0.0
    refiner_elapsed = 0.0
    expert_elapsed = 0.0

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
            base_start = time.time()
            try:
                base_result = _cached_base_result(query)
            except Exception:
                logger.exception("Base agent failed")
                return (
                    f"{_OLLAMA_ERROR_MESSAGE}\n"
                    "The base agent could not process your query."
                )
            base_elapsed = time.time() - base_start
            logger.info("Base agent completed in %.2fs", base_elapsed)

            elapsed = time.time() - pipeline_start
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
        base_start = time.time()
        try:
            base_result = _run_base(query)
        except Exception:
            logger.exception("Base agent failed")
            return (
                f"{_OLLAMA_ERROR_MESSAGE}\n"
                "The base agent could not process your query."
            )
        base_elapsed = time.time() - base_start
        logger.info("Base agent completed in %.2fs", base_elapsed)

        # 3. Decide: run refiner?
        refiner_error = False
        if should_run_refiner(base_result, level):
            refiner_start = time.time()
            try:
                base_result = _run_refiner(base_result)
                refiner_used = True
            except Exception:
                logger.exception("Refiner failed")
                refiner_error = True
            refiner_elapsed = time.time() - refiner_start
            logger.info("Refiner completed in %.2fs", refiner_elapsed)

        # 4. Decide: run expert?
        expert_error = False
        if should_run_expert(base_result, level):
            expert_start = time.time()
            try:
                base_result = _run_expert(base_result, query)
                expert_used = True
            except Exception:
                logger.exception("Expert failed")
                expert_error = True
            expert_elapsed = time.time() - expert_start
            logger.info("Expert completed in %.2fs", expert_elapsed)

        # 5. Extract final answer
        final_answer = base_result.answer
        if refiner_error:
            final_answer += "\n\n[Refiner step failed: the answer above may not be fully polished.]"
        if expert_error:
            final_answer += "\n\n[Expert step failed: the answer above may not include deep insights.]"

        # 6. Log execution statistics
        elapsed = time.time() - pipeline_start
        logger.info(
            (
                "Agents | complexity=%s | tokens=%d | confidence=%.2f | "
                "refiner=%s | expert=%s | "
                "base=%.2fs | refiner=%.2fs | expert=%.2fs | "
                "pipeline total=%.2fs"
            ),
            level,
            base_result.tokens,
            base_result.confidence,
            "yes" if refiner_used else "no",
            "yes" if expert_used else "no",
            base_elapsed,
            refiner_elapsed,
            expert_elapsed,
            elapsed,
        )

        return final_answer

    except Exception as exc:
        logger.exception("Agent pipeline failed unexpectedly")
        return (
            f"{_OLLAMA_ERROR_MESSAGE}\n"
            f"Error: {exc}"
        )
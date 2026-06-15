"""
agents/models.py
Data models for multi-agent system.

AgentResult encapsulates the output of each agent in the pipeline,
allowing metadata (confidence, tokens) to flow between stages.
"""

from dataclasses import dataclass
from typing import Final

__all__ = ["AgentResult"]


@dataclass(slots=True)
class AgentResult:
    """
    Result from an agent processing step.

    Attributes:
        answer: The generated response text.
        confidence: Confidence level (0.0 to 1.0). Higher = more confident.
        tokens: Approximate token count of the answer.
        should_refine: Whether refiner should process this result.
        should_expert: Whether expert should add insights.
    """

    answer: str
    confidence: float = 1.0
    tokens: int = 0
    should_refine: bool = True
    should_expert: bool = False

    def __post_init__(self) -> None:
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        if self.tokens < 0:
            raise ValueError(f"Tokens cannot be negative, got {self.tokens}")

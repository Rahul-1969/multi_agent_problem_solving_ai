"""
agents/refiner_agent.py
Thin wrapper that delegates refiner execution to the centralized
LLM implementation.
"""

from utils.logger import get_logger
from agents.llm_agents import run_refiner_agent
from agents.models import AgentResult

logger = get_logger(__name__)


def refine_answer(result: AgentResult) -> AgentResult:
    """
    Delegate refiner execution to the centralized implementation.
    """
    return run_refiner_agent(result)

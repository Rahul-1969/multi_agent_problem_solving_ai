"""
agents/base_agent.py
Thin wrapper that delegates base agent execution to the centralized
LLM implementation.
"""

from utils.logger import get_logger
from agents.llm_agents import run_base_agent
from agents.models import AgentResult

logger = get_logger(__name__)


def base_agent(query: str) -> AgentResult:
    """
    Delegate base agent execution to the centralized implementation.
    """
    return run_base_agent(query)

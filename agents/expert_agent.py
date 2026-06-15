"""
agents/expert_agent.py
Thin wrapper that delegates expert execution to the centralized
LLM implementation.
"""

from utils.logger import get_logger
from agents.llm_agents import run_expert_agent
from agents.models import AgentResult

logger = get_logger(__name__)


def expert_enhance(result: AgentResult, query: str) -> AgentResult:
    """
    Delegate expert execution to the centralized implementation.
    """
    return run_expert_agent(result, query)

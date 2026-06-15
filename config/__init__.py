"""Configuration package for the Multi-Agent AI Chatbot."""

from . import llm_config, college_config, path_config
from .llm_config import *
from .college_config import *
from .path_config import *

__all__ = [
    *llm_config.__all__,
    *college_config.__all__,
    *path_config.__all__,
]
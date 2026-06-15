"""Cache helpers for the Multi-Agent AI Chatbot."""

from functools import lru_cache
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def cached_llm_call(maxsize: int = 256) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that caches LLM calls by arguments."""
    return lru_cache(maxsize=maxsize)


def cached_response(maxsize: int = 256) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that caches general responses by arguments."""
    return lru_cache(maxsize=maxsize)

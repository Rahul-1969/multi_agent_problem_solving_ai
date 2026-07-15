"""Cache helpers for the Multi-Agent AI Chatbot."""

from functools import lru_cache
from typing import Any, Callable, ParamSpec, TypeVar
from collections import defaultdict
import threading

P = ParamSpec("P")
R = TypeVar("R")


def cached_response(maxsize: int = 256) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that caches general responses by arguments."""
    return lru_cache(maxsize=maxsize)


class _DomainCache:
    """Per-domain LRU cache with hit/miss tracking."""

    def __init__(self, domain: str, maxsize: int):
        self.domain = domain
        self.maxsize = maxsize
        self._cache = lru_cache(maxsize=maxsize)
        self._total_calls = 0
        self._misses = 0  # actual function executions
        self._lock = threading.Lock()

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        # Wrap the original function to count actual executions (misses)
        def counting_func(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._lock:
                self._misses += 1
            return func(*args, **kwargs)

        # Apply lru_cache to the counting wrapper
        cached_func = self._cache(counting_func)

        def tracking_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._lock:
                self._total_calls += 1
            return cached_func(*args, **kwargs)

        return tracking_wrapper

    def get_stats(self) -> dict[str, int]:
        with self._lock:
            hits = self._total_calls - self._misses
            return {"hits": hits, "misses": self._misses, "maxsize": self.maxsize}

    def cache_info(self):
        return self._cache.cache_info()


# Domain cache configurations
_DOMAIN_CACHE_CONFIG = {
    "general": 64,
    "education": 32,
    "coding": 48,
    "medical": 32,
    "": 64,  # agents and misc
}

_DOMAIN_CACHES: dict[str, _DomainCache] = {}
_DOMAIN_CACHES_LOCK = threading.Lock()


def _get_domain_cache(domain: str) -> _DomainCache:
    """Get or create the cache for a domain."""
    with _DOMAIN_CACHES_LOCK:
        if domain not in _DOMAIN_CACHES:
            maxsize = _DOMAIN_CACHE_CONFIG.get(domain, 64)
            _DOMAIN_CACHES[domain] = _DomainCache(domain, maxsize)
        return _DOMAIN_CACHES[domain]


def cached_llm_call(maxsize: int = 256) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Return a decorator that caches LLM calls by arguments with domain awareness.
    If domain is passed as a keyword argument, uses per-domain cache.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        # Store cached functions per domain (created lazily on first use)
        _cached_funcs: dict[str, Callable[P, R]] = {}
        _cached_funcs_lock = threading.Lock()

        def wrapper(*args: P.args, domain: str = "", **kwargs: P.kwargs) -> R:
            with _cached_funcs_lock:
                if domain not in _cached_funcs:
                    cache = _get_domain_cache(domain)
                    _cached_funcs[domain] = cache(func)
                cached_func = _cached_funcs[domain]
            return cached_func(*args, **kwargs)

        return wrapper
    return decorator


def get_cache_stats() -> dict[str, dict[str, int]]:
    """Returns hit/miss counts per domain."""
    with _DOMAIN_CACHES_LOCK:
        return {domain: cache.get_stats() for domain, cache in _DOMAIN_CACHES.items()}


def clear_domain_cache(domain: str) -> bool:
    """Clear a specific domain's cache. Returns True if domain existed."""
    with _DOMAIN_CACHES_LOCK:
        if domain in _DOMAIN_CACHES:
            # lru_cache doesn't have a clear method, so we recreate
            maxsize = _DOMAIN_CACHES[domain].maxsize
            _DOMAIN_CACHES[domain] = _DomainCache(domain, maxsize)
            return True
        return False
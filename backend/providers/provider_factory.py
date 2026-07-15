"""
backend/providers/provider_factory.py
Provider selection and instantiation.

Returns AIProvider instances (full interface).
Callers may type-narrow to a role interface (TextGenerationProvider, etc.)
if they only need a subset of capabilities — but this is optional; all
call-sites work unchanged with the AIProvider union type.

External API is unchanged: get_provider(task) -> AIProvider.
"""

import threading
from backend.providers.base_provider import AIProvider
from backend.providers.gemini_provider import GeminiProvider
from backend.providers.ollama_provider import OllamaProvider
from config.provider_config import (
    PROVIDER_TITLE,
    PROVIDER_LIVE,
    PROVIDER_ENRICH,
    PROVIDER_CLASSIFIER,
    PROVIDER_CAREER,
    PROVIDER_SCHOLARSHIP,
    PROVIDER_COMPARE
)

_providers: dict[str, AIProvider] = {}
_lock = threading.Lock()

def _instantiate_provider(name: str) -> AIProvider:
    if name == "gemini-flash":
        return GeminiProvider(tier="flash")
    elif name == "gemini-pro":
        return GeminiProvider(tier="pro")
    elif name == "ollama":
        return OllamaProvider()
    else:
        # Default fallback
        return OllamaProvider()

def get_provider(task: str) -> AIProvider:
    """
    Returns the configured AIProvider for a given task.

    Tasks: 'title', 'live', 'enrich', 'classify', 'career', 'scholarship', 'compare'

    The returned object satisfies the full AIProvider interface.
    Type-narrow with isinstance() to a role interface if needed:

        provider = get_provider("classify")
        if isinstance(provider, ClassificationProvider):
            ...
    """
    task_mapping = {
        "title": PROVIDER_TITLE,
        "live": PROVIDER_LIVE,
        "enrich": PROVIDER_ENRICH,
        "classify": PROVIDER_CLASSIFIER,
        "career": PROVIDER_CAREER,
        "scholarship": PROVIDER_SCHOLARSHIP,
        "compare": PROVIDER_COMPARE,
        "gemini": "gemini-flash"  # alias for backward compatibility
    }

    provider_name = task_mapping.get(task, "ollama")

    if provider_name not in _providers:
        with _lock:
            if provider_name not in _providers:
                _providers[provider_name] = _instantiate_provider(provider_name)

    return _providers[provider_name]

def get_provider_status() -> dict[str, str]:
    """
    Returns the status of all configured providers.
    """
    # Get all unique provider names from task mapping
    task_mapping = {
        "title": PROVIDER_TITLE,
        "live": PROVIDER_LIVE,
        "enrich": PROVIDER_ENRICH,
        "classify": PROVIDER_CLASSIFIER,
        "career": PROVIDER_CAREER,
        "scholarship": PROVIDER_SCHOLARSHIP,
        "compare": PROVIDER_COMPARE
    }
    all_provider_names = set(task_mapping.values())
    
    status = {}
    with _lock:
        for name in all_provider_names:
            if name in _providers:
                status[name] = "initialized"
            else:
                status[name] = "not_initialized"
    return status

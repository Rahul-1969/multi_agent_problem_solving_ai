"""
backend/providers/base_provider.py
AI Provider abstraction — Interface Segregation Principle.

Design
------
Four narrow role interfaces cover the actual capability boundaries:

    TextGenerationProvider  — generate(), generate_title()
    ClassificationProvider  — classify()
    EnrichmentProvider      — enrich_batch(), compare_colleges()
    LiveProvider            — live_answer()

AIProvider is the full union (all four roles).  Providers that lack a
capability still satisfy the interface via the safe default stubs defined
here, so zero call-sites change and the ProviderFactory contract is unchanged.

Ollama implements the two universal roles natively.
GeminiProvider implements all four roles natively.

                    AIProvider
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
TextGeneration  Classification    EnrichmentProvider
Provider           Provider          LiveProvider

Backward compatibility
----------------------
All existing imports of `AIProvider` and `AIResult` continue to work.
`from backend.providers.base_provider import AIProvider, AIResult`
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict


# ── Shared result container ────────────────────────────────────────────────────

@dataclass
class AIResult:
    """Unified result container returned by every provider method."""
    content: str
    sources: List[str]
    verified_date: Optional[str]
    cached: bool
    provider: str           # "gemini-flash" | "gemini-pro" | "ollama"
    latency_ms: float
    tokens_used: Optional[int]


# ── Role interfaces ────────────────────────────────────────────────────────────

class TextGenerationProvider(ABC):
    """
    Universal capability — every provider must be able to generate text
    and produce a short title for a conversation.
    Implemented by: GeminiProvider, OllamaProvider.
    """

    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> AIResult:
        """Generate a free-form text response."""

    @abstractmethod
    def generate_title(self, message: str) -> str:
        """Return a short (≤ 6 word) chat title derived from *message*."""


class ClassificationProvider(ABC):
    """
    Universal capability — classify a prompt into one of a fixed label set.
    Implemented by: GeminiProvider, OllamaProvider (primary).
    """

    @abstractmethod
    def classify(self, prompt: str) -> str:
        """Return a single classification label string."""


class LiveProvider(ABC):
    """
    Gemini-specific capability — answer queries that need current / live
    information, optionally using Google Search grounding.
    OllamaProvider provides a safe fallback stub via AIProvider.
    """

    @abstractmethod
    def live_answer(
        self,
        query: str,
        context: str = "",
        use_grounding: bool = True,
    ) -> Optional[AIResult]:
        """
        Return an AIResult with live / grounded answer, or None on failure.
        Providers that cannot satisfy this must return None.
        """


class EnrichmentProvider(ABC):
    """
    Gemini-specific capability — bulk metadata enrichment and structured
    comparison of college records.
    OllamaProvider provides safe no-op stubs via AIProvider.
    """

    @abstractmethod
    def enrich_batch(self, colleges: List[str]) -> Dict[str, Dict]:
        """
        Enrich a batch of college codes with AI-generated metadata.
        Returns a dict keyed by college code.  Empty dict on failure.
        """

    @abstractmethod
    def compare_colleges(
        self,
        codes: List[str],
        profile: Dict,
    ) -> Optional[AIResult]:
        """
        Return a structured comparison of the given college codes for a
        student profile, or None on failure.
        """


# ── Full provider interface ────────────────────────────────────────────────────

class AIProvider(
    TextGenerationProvider,
    ClassificationProvider,
    LiveProvider,
    EnrichmentProvider,
):
    """
    Full AI provider interface — composition of all four role interfaces.

    Every concrete provider (Gemini, Ollama, …) implements this class.
    Providers that lack a capability must still satisfy the abstract methods
    — they should return a safe empty value (None / {}) as documented on
    each role interface.

    The ProviderFactory always returns AIProvider, so call-sites need only
    know about the role they actually use; they are free to type-narrow with
    isinstance() or Protocol checks if needed.
    """

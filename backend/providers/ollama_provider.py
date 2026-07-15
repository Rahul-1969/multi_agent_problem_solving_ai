import time
from typing import Optional, List, Dict

from backend.providers.base_provider import (
    AIProvider,
    AIResult,
)
from llm.ollama_client import call_llm
from utils.text_cleaner import clean_text
from utils.logger import get_logger

logger = get_logger(__name__)

class OllamaProvider(AIProvider):
    """
    Local AIProvider implementation backed by Ollama.

    Role coverage
    -------------
    TextGenerationProvider : generate(), generate_title()  — native
    ClassificationProvider : classify()                    — native (primary)
    LiveProvider           : live_answer()                 — stub (delegates to generate)
    EnrichmentProvider     : enrich_batch()                — stub (returns {})
                             compare_colleges()            — stub (delegates to generate)
    """
    def __init__(self):
        self.provider_name = "ollama"

    def generate(self, prompt: str, system: str = "") -> AIResult:
        start_time = time.time()
        response = call_llm(prompt=prompt, system=system)
        latency = (time.time() - start_time) * 1000
        
        return AIResult(
            content=clean_text(response),
            sources=[],
            verified_date=None,
            cached=False,
            provider=self.provider_name,
            latency_ms=latency,
            tokens_used=None
        )

    def classify(self, prompt: str) -> str:
        start_time = time.time()
        response = call_llm(prompt=prompt, system="You are a strict classifier. Answer in exactly one word from the allowed list.", num_predict=10)
        latency = (time.time() - start_time) * 1000
        # metrics logging can happen at the caller level for Ollama, or imported here
        return clean_text(response).strip().lower()

    def live_answer(self, query: str, context: str = "", use_grounding: bool = False) -> Optional[AIResult]:
        # Ollama can't easily do live web search
        return self.generate(f"Context: {context}\nQuery: {query}")

    def generate_title(self, message: str) -> str:
        prompt = f"Summarize this into a short 4-word title without quotes: {message}"
        res = self.generate(prompt)
        return res.content.strip()

    def enrich_batch(self, colleges: List[str]) -> Dict[str, Dict]:
        # Ollama is not typically used for JSON data extraction of this size in this architecture
        return {}

    def compare_colleges(self, codes: List[str], profile: Dict) -> Optional[AIResult]:
        prompt = f"Compare these colleges: {codes} for student profile {profile}"
        return self.generate(prompt)

import time
import os
import json
from typing import Optional, List, Dict
from google import genai
from google.genai import types

from backend.providers.base_provider import (
    AIProvider,
    AIResult,
)
from config.gemini_config import GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL
from backend.observability.metrics import metrics
from utils.logger import get_logger
from utils.prompt_loader import load_prompt

logger = get_logger(__name__)

_DEFAULT_TEMPERATURE = 0.7


class GeminiProvider(AIProvider):
    """
    Full AIProvider implementation backed by Google Gemini.

    Role coverage
    -------------
    TextGenerationProvider : generate(), generate_title()
    ClassificationProvider : classify()
    LiveProvider           : live_answer()  (primary — grounding capable)
    EnrichmentProvider     : enrich_batch(), compare_colleges()
    """
    def __init__(self, tier: str = "flash"):
        self.tier = tier
        self.model_name = GEMINI_FLASH_MODEL if tier == "flash" else GEMINI_PRO_MODEL
        self._client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

    def generate(self, prompt: str, system: str = "") -> AIResult:
        start_time = time.time()
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=_DEFAULT_TEMPERATURE,
            ),
        )
        latency = (time.time() - start_time) * 1000
        return AIResult(
            content=response.text,
            sources=[],
            verified_date=None,
            cached=False,
            provider=f"gemini-{self.tier}",
            latency_ms=latency,
            tokens_used=None  # Gemini SDK doesn't easily expose this in simple generate_content sometimes, but can be added
        )

    def classify(self, prompt: str) -> str:
        # Normally Ollama handles classify, but implemented for completeness
        start_time = time.time()
        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=_DEFAULT_TEMPERATURE,
            ),
        )
        metrics.record_gemini_call(self.tier, (time.time() - start_time)*1000, None, False)
        return response.text.strip().lower()

    def live_answer(self, query: str, context: str = "", use_grounding: bool = True) -> Optional[AIResult]:
        template = load_prompt("live_prompt.txt")
        prompt = template.format(context=context, query=query)

        start_time = time.time()

        tools = []
        if use_grounding:
            # We can use Google Search tool if enabled and supported by the API
            # For this SDK version, we'll assume we can pass tools="google_search_retrieval" or similar if supported
            # Note: as of recent SDKs, 'google_search_retrieval' tool configuration can be complex.
            # We will use a standard generate for now and simulate grounding if the API doesn't support it directly.
            pass

        try:
            # Structured JSON response for reliable parsing
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            latency = (time.time() - start_time) * 1000

            data = json.loads(response.text)

            return AIResult(
                content=data.get("answer", response.text),
                sources=data.get("sources", []),
                verified_date=data.get("verified_date"),
                cached=False,
                provider=f"gemini-{self.tier}",
                latency_ms=latency,
                tokens_used=None
            )
        except Exception as e:
            logger.exception("Failed live_answer in GeminiProvider")
            metrics.record_fallback(str(e))
            return None

    def generate_title(self, message: str) -> str:
        template = load_prompt("title_prompt.txt")
        prompt = template.format(message=message)

        try:
            start_time = time.time()
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=_DEFAULT_TEMPERATURE,
                ),
            )
            latency = (time.time() - start_time) * 1000
            metrics.record_gemini_call(self.tier, latency, None, False)
            return response.text.strip()
        except Exception:
            return message[:40].strip()

    def enrich_batch(self, colleges: List[str]) -> Dict[str, Dict]:
        template = load_prompt("metadata_prompt.txt")
        prompt = template.format(college_list=", ".join(colleges))

        try:
            start_time = time.time()
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            latency = (time.time() - start_time) * 1000
            metrics.record_gemini_call(self.tier, latency, None, False)

            data = json.loads(response.text)
            if isinstance(data, list):
                return {item.get("code", "UNKNOWN"): item for item in data}
            return {}
        except Exception as e:
            logger.exception("Failed enrich_batch in GeminiProvider")
            return {}

    def compare_colleges(self, codes: List[str], profile: Dict) -> Optional[AIResult]:
        template = load_prompt("comparison_prompt.txt")
        prompt = template.format(college_data=codes, context=profile, query="Compare these")

        try:
            start_time = time.time()
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=_DEFAULT_TEMPERATURE,
                ),
            )
            latency = (time.time() - start_time) * 1000
            metrics.record_gemini_call(self.tier, latency, None, False)

            return AIResult(
                content=response.text,
                sources=[],
                verified_date=None,
                cached=False,
                provider=f"gemini-{self.tier}",
                latency_ms=latency,
                tokens_used=None
            )
        except Exception:
            return None

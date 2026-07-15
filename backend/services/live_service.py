from typing import Optional
from backend.providers.provider_factory import get_provider
from backend.providers.base_provider import AIResult
from backend.cache.gemini_cache import gemini_cache
from backend.cache.usage_tracker import usage_tracker
from backend.observability.metrics import metrics
from config.ai_features import ENABLE_GROUNDING
from config.gemini_config import GEMINI_FLASH_MODEL, CACHE_TTL_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)

def get_live_answer(query: str, username: str, context: str = "") -> Optional[AIResult]:
    """
    Fetches a live answer using the configured provider (default gemini-flash).
    Applies caching and usage tracking.
    """
    if not usage_tracker.can_use(username, "flash"):
        logger.warning(f"User {username} reached flash limits.")
        return None
        
    # Check cache
    cached_content = gemini_cache.get(query, GEMINI_FLASH_MODEL)
    if cached_content:
        metrics.record_cache_hit("live")
        return AIResult(
            content=cached_content,
            sources=[],
            verified_date=None,
            cached=True,
            provider="gemini-flash",
            latency_ms=0,
            tokens_used=0
        )
        
    # Fetch from provider
    provider = get_provider("live")
    result = provider.live_answer(query, context, use_grounding=ENABLE_GROUNDING)
    
    if result:
        gemini_cache.set(query, GEMINI_FLASH_MODEL, result.content, CACHE_TTL_SECONDS)
        usage_tracker.record_use(username, "flash")
        # Metrics already recorded in GeminiProvider for latency, we record the successful tier call there
        
    return result

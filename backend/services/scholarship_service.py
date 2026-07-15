from typing import Optional
from backend.providers.provider_factory import get_provider
from backend.providers.base_provider import AIResult
from backend.cache.gemini_cache import gemini_cache
from backend.cache.usage_tracker import usage_tracker
from backend.observability.metrics import metrics

from utils.logger import get_logger
from utils.prompt_loader import load_prompt
from config.gemini_config import GEMINI_FLASH_MODEL, CACHE_TTL_SECONDS

logger = get_logger(__name__)

def get_scholarship_info(query: str, username: str, context: str = "") -> Optional[AIResult]:
    """
    Fetches scholarship info using the configured provider.
    """
    if not usage_tracker.can_use(username, "flash"):
        logger.warning(f"User {username} reached flash limits.")
        return None
        
    cache_key = f"scholarship:{query}"
    cached_content = gemini_cache.get(cache_key, GEMINI_FLASH_MODEL)
    if cached_content:
        metrics.record_cache_hit("scholarship")
        return AIResult(
            content=cached_content,
            sources=[],
            verified_date=None,
            cached=True,
            provider="gemini-flash",
            latency_ms=0,
            tokens_used=0
        )
        
    provider = get_provider("scholarship")
    
    # Read prompt
    template = load_prompt("scholarship_prompt.txt")
    if template:
        formatted_prompt = template.format(context=context, query=query)
    else:
        # Fallback if prompt file is missing
        formatted_prompt = f"Scholarship query: {query}\nContext: {context}"
    
    result = provider.generate(prompt=formatted_prompt, system="You are an expert scholarship counselor.")
    
    if result:
        gemini_cache.set(cache_key, GEMINI_FLASH_MODEL, result.content, CACHE_TTL_SECONDS)
        usage_tracker.record_use(username, "flash")
        
    return result

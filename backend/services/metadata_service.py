from typing import Dict, Any
from backend.providers.provider_factory import get_provider
from utils.logger import get_logger
from config.ai_features import ENABLE_COLLEGE_ENRICH

logger = get_logger(__name__)

def enrich_missing_fields(card: Dict[str, Any]) -> Dict[str, Any]:
    """
    Called only when ENABLE_COLLEGE_ENRICH is True.
    Normally for real-time missing field enrichment, but usually handled by metadata_refresher offline.
    """
    if not ENABLE_COLLEGE_ENRICH:
        return card
        
    code = card.get("code")
    if not code:
        return card
        
    provider = get_provider("enrich")
    try:
        enriched_data = provider.enrich_batch([code])
        if code in enriched_data:
            # Merge fields that were null
            for k, v in enriched_data[code].items():
                if card.get(k) is None and v is not None:
                    card[k] = v
    except Exception as e:
        logger.error(f"Failed to enrich college {code}: {e}")
        
    return card

from backend.providers.provider_factory import get_provider
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_title(message: str) -> str:
    """
    Generates a short chat title from the first message.
    Safe fallback to message snippet on failure.
    """
    provider = get_provider("title")
    try:
        title = provider.generate_title(message)
        if title:
            return title
    except Exception as e:
        logger.error(f"Failed to generate title: {e}")
        
    return message[:40].strip()

from pipelines.pipeline_result import PipelineResult
from backend.services.live_service import get_live_answer
from backend.models.response_models import GeneralData
from config.ai_features import ENABLE_LIVE_PIPELINE
from pipelines.general_pipeline import general_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

def process_query(query: str, chat_history: list = None, **kwargs) -> PipelineResult:
    """
    Handles live queries using Gemini (news, rankings, AI trends, etc.).
    Falls back to local general pipeline if Gemini is disabled or fails.
    """
    if not ENABLE_LIVE_PIPELINE:
        return general_pipeline(query, chat_history, **kwargs)
        
    username = kwargs.get("username", "anonymous")
    context = "" # Ideally extract from chat history
    
    result = get_live_answer(query, username, context)
    
    if result:
        return PipelineResult(
            response=result.content,
            data=GeneralData(answer=result.content),
        )
    else:
        # Fallback to local
        logger.warning("Live pipeline failed, falling back to local.")
        return general_pipeline(query, chat_history, **kwargs)

from pipelines.pipeline_result import PipelineResult
from backend.services.scholarship_engine import process_scholarship_request
from backend.auth.user_store import user_store
from config.ai_features import ENABLE_SCHOLARSHIP_PIPELINE
from pipelines.general_pipeline import general_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

def process_query(query: str, chat_history: list = None, **kwargs) -> PipelineResult:
    """
    Handles scholarship queries deterministically, enriched by Gemini.
    """
    if not ENABLE_SCHOLARSHIP_PIPELINE:
        return general_pipeline(query, chat_history, **kwargs)
        
    username = kwargs.get("username", "anonymous")
    user = user_store.get_user(username)
    profile = user.get("profile", {}) if user else {}
    
    scholarship_data = process_scholarship_request(profile)
    
    if scholarship_data and scholarship_data.scholarships:
        logger.info(
            "Scholarship pipeline matched results | username=%s matches=%d",
            username,
            len(scholarship_data.scholarships),
        )
        return PipelineResult(
            response=f"Found {len(scholarship_data.scholarships)} scholarships matching your profile.",
            data=scholarship_data,
        )
    else:
        logger.warning(
            "Scholarship pipeline found no matches for user, falling back to local | username=%s",
            username,
        )
        return general_pipeline(query, chat_history, **kwargs)


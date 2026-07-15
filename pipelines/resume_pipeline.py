from pipelines.pipeline_result import PipelineResult
from backend.services.resume_service import analyze_resume_text
from config.ai_features import ENABLE_CAREER_PIPELINE
from pipelines.general_pipeline import general_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

def process_query(query: str, chat_history: list = None, **kwargs) -> PipelineResult:
    """
    Handles plain text resume analysis via chat.
    For PDF, use the dedicated /api/v1/resume/analyze endpoint.
    """
    if not ENABLE_CAREER_PIPELINE:
        return general_pipeline(query, chat_history, **kwargs)
        
    resume_data = analyze_resume_text(query)
    
    return PipelineResult(
        response=f"I've analyzed your resume text. Your ATS score is {resume_data.ats_score}.",
        data=resume_data
    )

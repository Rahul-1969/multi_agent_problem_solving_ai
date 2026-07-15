from pipelines.pipeline_result import PipelineResult
from backend.services.roadmap_engine import generate_roadmap, regenerate_node
from config.ai_features import ENABLE_CAREER_PIPELINE
from pipelines.general_pipeline import general_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

def process_query(query: str, chat_history: list = None, **kwargs) -> PipelineResult:
    """
    Handles career queries and roadmap generation using Gemini.
    """
    if not ENABLE_CAREER_PIPELINE:
        return general_pipeline(query, chat_history, **kwargs)
        
    username = kwargs.get("username", "anonymous")
    
    # Check if this is a partial regeneration request
    # E.g., kwargs might contain 'node_title' and 'feedback'
    node_title = kwargs.get("node_title")
    feedback = kwargs.get("feedback")
    current_roadmap = kwargs.get("current_roadmap")
    
    if node_title and feedback and current_roadmap:
        roadmap_data = regenerate_node(node_title, feedback, current_roadmap)
        return PipelineResult(
            response=f"Updated node {node_title}",
            data=roadmap_data,
        )
        
    roadmap_data = generate_roadmap(query)
    
    if roadmap_data and roadmap_data.roadmap_steps:
        logger.info(
            "Career roadmap generated successfully | query=%s steps=%d",
            query[:80],
            len(roadmap_data.roadmap_steps),
        )
        return PipelineResult(
            response="Here is your personalized career roadmap.",
            data=roadmap_data,
        )
    else:
        logger.warning(
            "Career pipeline returned empty roadmap, falling back to local | query=%s",
            query[:80],
        )
        return general_pipeline(query, chat_history, **kwargs)


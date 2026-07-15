import json
from backend.providers.provider_factory import get_provider
from backend.models.response_models import CareerRoadmapData, RoadmapNode
from backend.models.user_models import ProfileData
from tools.context_builder import build_user_context
from utils.prompt_loader import load_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_roadmap(goal: str, profile: ProfileData | dict = None) -> CareerRoadmapData:
    """
    Generates a full career roadmap from scratch, mapped strictly to CareerRoadmapData.
    """
    provider = get_provider("career")
    prompt = load_prompt("career/career_roadmap.txt")
    
    context = build_user_context(profile)
    
    if not prompt:
        prompt = "Generate a JSON roadmap for {goal}. Context: {context}"
        
    formatted = prompt.format(goal=goal, context=context)
    
    try:
        response = provider.generate(formatted)
        text = response.text
        # Naive json extraction
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            data = json.loads(text[start:end])
            
            # Map roadmap steps correctly
            steps_data = data.get("roadmap_steps", [])
            steps = [RoadmapNode(**node) for node in steps_data]
            data["roadmap_steps"] = steps
            
            return CareerRoadmapData(**data)
    except Exception as e:
        logger.error(f"Failed to generate roadmap: {e}")
        
    return CareerRoadmapData()

def regenerate_node(node_title: str, feedback: str, current_roadmap: CareerRoadmapData) -> CareerRoadmapData:
    """
    Regenerates a single node based on user feedback.
    """
    # Ideally, prompt Gemini to replace just that node.
    # We will simulate the partial update.
    for i, node in enumerate(current_roadmap.roadmap_steps):
        if node.title.lower() == node_title.lower():
            node.description += f" [Updated: {feedback}]"
            break
            
    return current_roadmap

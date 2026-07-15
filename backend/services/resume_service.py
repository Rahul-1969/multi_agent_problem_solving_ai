import json
from backend.providers.provider_factory import get_provider
from backend.models.response_models import ResumeData
from utils.prompt_loader import load_prompt
from tools.resume_parser import parse_resume
from tools.ats_scorer import score_ats
from utils.logger import get_logger

logger = get_logger(__name__)

def analyze_resume_text(raw_text: str) -> ResumeData:
    """
    Analyzes resume text through the deterministic pipeline and Gemini suggestions.
    """
    # 1. Deterministic parsing
    parsed = parse_resume(raw_text)
    
    # 2. Deterministic scoring
    score, missing = score_ats(parsed)
    
    # 3. Gemini suggestions
    gemini_data = {
        "grammar_issues": [],
        "weak_bullet_points": [],
        "formatting_suggestions": [],
        "suggested_certifications": [],
        "suggested_improvements": [],
        "future_ready_skills": []
    }
    provider = get_provider("enrich")
    prompt = load_prompt("resume/resume_suggestions.txt")
    
    if not prompt:
        prompt = "Provide suggestions in JSON for this resume: {parsed_text}"
        
    formatted = prompt.format(parsed_text=json.dumps(parsed))
    
    try:
        response = provider.generate(formatted)
        if response and response.content:
            text = response.content
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                try:
                    gemini_data = json.loads(text[start:end])
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from resume suggestions response")
    except Exception as e:
        logger.error(f"Failed to generate resume suggestions: {e}")
        
    # 4. Construct response
    return ResumeData(
        ats_score=score,
        resume_summary=parsed.get("resume_summary", ""),
        detected_skills=parsed.get("detected_skills", []),
        education=parsed.get("education", []),
        experience=parsed.get("experience", []),
        projects=parsed.get("projects", []),
        missing_skills=missing,
        grammar_issues=gemini_data.get("grammar_issues", []),
        weak_bullet_points=gemini_data.get("weak_bullet_points", []),
        formatting_suggestions=gemini_data.get("formatting_suggestions", []),
        suggested_certifications=gemini_data.get("suggested_certifications", []),
        suggested_improvements=gemini_data.get("suggested_improvements", []),
        future_ready_skills=gemini_data.get("future_ready_skills", [])
    )

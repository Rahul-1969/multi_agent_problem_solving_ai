import json
from backend.models.user_models import ProfileData
from backend.models.response_models import ResumeMatchData
from tools.document_extractor import DocumentExtractor
from tools.resume_parser import parse_resume
from tools.ats_scorer import score_ats
from tools.job_description_parser import parse_job_description
from tools.resume_matching_engine import compute_resume_match
from backend.providers.provider_factory import get_provider
from tools.context_builder import build_user_context

def analyze_resume_match(file_path: str, filename: str, jd_text: str, profile: ProfileData | None = None) -> ResumeMatchData:
    """
    Complete Resume Matching pipeline.
    """
    
    # 1. Extract text from Resume
    resume_text = DocumentExtractor.extract_text(file_path, filename)
    
    # 2. Parse Resume
    parsed_resume_dict = parse_resume(resume_text)
    
    # 3. ATS Score Resume
    ats_score, missing = score_ats(parsed_resume_dict)
    
    from backend.models.response_models import ResumeData
    resume_data = ResumeData(
        ats_score=ats_score,
        resume_summary=parsed_resume_dict.get("resume_summary", ""),
        detected_skills=parsed_resume_dict.get("detected_skills", []),
        missing_skills=missing,
        experience=parsed_resume_dict.get("experience", []),
        education=parsed_resume_dict.get("education", []),
        projects=parsed_resume_dict.get("projects", [])
    )
    
    # 4. Parse JD
    jd_data = parse_job_description(jd_text)
    
    # 5. Deterministic Matching Engine
    match_data = compute_resume_match(resume_data, jd_data)
    
    # 6. Gemini Suggestions for improvements based on gaps
    provider = get_provider("enrich")
    
    context = build_user_context(profile) if profile else "No profile provided."
    
    prompt = f"""
    You are an expert career counselor.
    
    User Context:
    {context}
    
    Resume Gaps vs Job Description:
    - Missing Skills: {', '.join(match_data.missing_skills)}
    - Experience Gap: {match_data.experience_gap or 'None'}
    - Education Gap: {match_data.education_gap or 'None'}
    - Certification Gap: {match_data.certification_gap or 'None'}
    
    Explain these gaps briefly and suggest 2 specific recommended courses and 2 specific projects the user can build to bridge these gaps.
    
    Output strictly as JSON:
    {{
        "gemini_suggestions": "A paragraph explaining the gaps.",
        "recommended_courses": ["Course 1", "Course 2"],
        "recommended_projects": ["Project 1", "Project 2"]
    }}
    """
    
    try:
        gemini_resp = provider.generate(prompt).content
        if "```json" in gemini_resp:
            gemini_resp = gemini_resp.split("```json")[1].split("```")[0].strip()
        elif "```" in gemini_resp:
            gemini_resp = gemini_resp.split("```")[1].strip()
            
        gemini_json = json.loads(gemini_resp)
        match_data.gemini_suggestions = gemini_json.get("gemini_suggestions")
        match_data.recommended_courses = gemini_json.get("recommended_courses", [])
        match_data.recommended_projects = gemini_json.get("recommended_projects", [])
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON from resume matching response")
        match_data.gemini_suggestions = "Could not generate AI suggestions."
    except Exception:
        match_data.gemini_suggestions = "Could not generate AI suggestions."
        
    return match_data

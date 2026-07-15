import json
from backend.models.user_models import ProfileData
from backend.models.response_models import ResumeData
from tools.document_extractor import DocumentExtractor
from tools.resume_parser import parse_resume
from tools.ats_scorer import score_ats
from tools.job_description_parser import parse_job_description
from tools.resume_matching_engine import compute_resume_match
from backend.providers.provider_factory import get_provider
from tools.context_builder import build_user_context
from backend.services.pipeline_dispatcher import PipelineResult

class ResumeMatchPipeline:
    @staticmethod
    def execute(file_path: str, filename: str, jd_text: str, profile: ProfileData | None = None) -> PipelineResult:
        """
        Executes the Resume Match workflow independently.
        """
        # 1. Extract Document Text
        resume_text = DocumentExtractor.extract_text(file_path, filename)
        
        # 2. Parse Resume Deterministically
        parsed_resume_dict = parse_resume(resume_text)
        
        # 3. ATS Scoring
        ats_score, missing = score_ats(parsed_resume_dict)
        
        resume_data = ResumeData(
            ats_score=ats_score,
            resume_summary=parsed_resume_dict.get("resume_summary", ""),
            detected_skills=parsed_resume_dict.get("detected_skills", []),
            missing_skills=missing,
            experience=parsed_resume_dict.get("experience", []),
            education=parsed_resume_dict.get("education", []),
            projects=parsed_resume_dict.get("projects", [])
        )
        
        # 4. Job Description Parsing
        jd_data = parse_job_description(jd_text)
        
        # 5. Deterministic Matching Engine
        match_data = compute_resume_match(resume_data, jd_data)
        
        # 6. Gemini Suggestions
        provider = get_provider("enrich")
        context = build_user_context(profile) if profile else "No user profile."
        
        prompt = f"""
        You are an expert career counselor helping a user bridge gaps in their resume to match a job description.
        
        User Context: {context}
        
        Gaps Identified Deterministically:
        - Missing Skills: {', '.join(match_data.missing_skills) if match_data.missing_skills else 'None'}
        - Experience Gap: {match_data.experience_gap or 'None'}
        - Education Gap: {match_data.education_gap or 'None'}
        - Certification Gap: {match_data.certification_gap or 'None'}
        
        Please provide tailored advice explaining these gaps and suggesting how to improve the resume, what to learn, and how to prepare for interviews.
        
        Output strictly as JSON:
        {{
            "gemini_suggestions": "Brief paragraph explaining the gaps and improvements.",
            "recommended_courses": ["Course 1", "Course 2"],
            "recommended_projects": ["Project 1", "Project 2"],
            "learning_roadmap": "Short roadmap to acquire missing skills.",
            "interview_preparation": "Specific interview tips based on the job description."
        }}
        """
        
        gemini_resp = provider.generate(prompt)
        try:
            if "```json" in gemini_resp:
                gemini_resp = gemini_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in gemini_resp:
                gemini_resp = gemini_resp.split("```")[1].strip()
                
            gemini_json = json.loads(gemini_resp)
            match_data.gemini_suggestions = gemini_json.get("gemini_suggestions")
            # We don't overwrite recommended courses if the model isn't using them, 
            # but we can pass them in the PipelineResult response markdown
        except Exception:
            match_data.gemini_suggestions = "Failed to generate AI suggestions."
            
        markdown_response = f"""# Resume Match Analysis
**Overall Match Score:** {match_data.overall_match_score}%

## Suggestions
{match_data.gemini_suggestions}
"""
        return PipelineResult(response=markdown_response, data=match_data.model_dump())

import pytest
from backend.models.response_models import ResumeData, JobDescriptionData
from tools.resume_matching_engine import compute_resume_match

def test_compute_resume_match():
    resume = ResumeData(
        detected_skills=["Python", "React"],
        experience=[{"detail": "Worked as a software engineer for 2 years"}],
        education=[{"detail": "B.Tech in Computer Science"}]
    )
    
    jd = JobDescriptionData(
        required_skills=["Python", "Java"],
        experience="2+ years",
        education="Bachelor's Degree",
        certifications=[]
    )
    
    match = compute_resume_match(resume, jd)
    
    assert "Python" in match.matched_skills
    assert "Java" in match.missing_skills
    assert match.experience_gap is None
    assert match.education_gap is None
    assert match.overall_match_score > 0

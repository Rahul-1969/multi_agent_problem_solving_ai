import pytest
from tools.resume_parser import parse_resume
from tools.ats_scorer import score_ats

def test_resume_parser_heuristics():
    text = """
    Summary
    I am a software engineer.
    
    Skills
    Python, React, Node.js
    
    Experience
    SDE at Google
    
    Education
    B.Tech in CS
    
    Projects
    AI Chatbot
    """
    
    parsed = parse_resume(text)
    assert "Python" in parsed["detected_skills"]
    assert len(parsed["experience"]) == 1
    assert "SDE at Google" in parsed["experience"][0]["detail"]
    assert "software engineer" in parsed["resume_summary"].lower()
    
def test_ats_scorer():
    parsed = {
        "detected_skills": ["Python"],
        "experience": [{"detail": "Job"}],
        "education": [],
        "projects": [{"detail": "Proj"}]
    }
    
    score, missing = score_ats(parsed)
    assert score == 30 + 40 + 10 # skills + exp + proj = 80
    assert len(missing) == 1
    assert "education" in missing[0].lower()

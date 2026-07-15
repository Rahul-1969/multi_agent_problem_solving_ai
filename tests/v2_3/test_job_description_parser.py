import pytest
from tools.job_description_parser import parse_job_description

def test_parse_job_description():
    jd_text = """
    We are looking for a Software Engineer.
    Required skills: Python, React, AWS, Docker.
    Preferred skills: Kubernetes.
    Minimum 5 years of experience required.
    Must have a Bachelor's Degree in Computer Science.
    PMP Certification is a plus.
    Excellent communication and teamwork skills needed.
    """
    data = parse_job_description(jd_text)
    
    assert "Python" in data.required_skills
    assert "React" in data.required_skills
    assert "Aws" in data.required_skills
    
    assert data.experience == "5+ years"
    assert "Bachelor's Degree" in data.education
    assert "PMP" in data.certifications
    assert "Communication" in data.soft_skills

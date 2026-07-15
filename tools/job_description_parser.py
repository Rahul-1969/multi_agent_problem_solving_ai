import re
from backend.models.response_models import JobDescriptionData

def parse_job_description(jd_text: str) -> JobDescriptionData:
    """
    Deterministically parses a job description text to extract requirements.
    """
    text = jd_text.lower()
    
    # 1. Experience matching
    experience_years = None
    exp_match = re.search(r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?(?:\s*of)?\s*experience', text)
    if exp_match:
        experience_years = f"{exp_match.group(1)}+ years"
        
    # 2. Education matching
    education_req = []
    if "bachelor" in text or "b.s" in text or "b.a" in text or "degree" in text:
        education_req.append("Bachelor's Degree")
    if "master" in text or "m.s" in text or "m.a" in text:
        education_req.append("Master's Degree")
    if "phd" in text or "ph.d" in text or "doctorate" in text:
        education_req.append("PhD")
        
    education = ", ".join(education_req) if education_req else None
    
    # 3. Skills matching (Basic heuristics)
    common_skills = [
        "python", "java", "javascript", "react", "node.js", "aws", "azure",
        "gcp", "docker", "kubernetes", "sql", "nosql", "machine learning",
        "deep learning", "agile", "scrum", "git", "ci/cd", "linux", "c++", "c#"
    ]
    
    required_skills = []
    for skill in common_skills:
        if skill in text:
            required_skills.append(skill.title())
            
    # Simple heuristic to split into required vs preferred based on position in text
    preferred_skills = []
    req_index = text.find("requirement")
    pref_index = text.find("preferred")
    if pref_index != -1 and req_index != -1 and pref_index > req_index:
        # Just an approximation: if it appears after "preferred", maybe it's preferred
        pass # To keep it simple, we will just dump them into required_skills for deterministic simplicity, or leave preferred_skills empty unless specified.

    # 4. Certifications
    certifications = []
    if "aws certified" in text: certifications.append("AWS Certification")
    if "pmp" in text: certifications.append("PMP")
    if "cissp" in text: certifications.append("CISSP")
    
    # 5. Soft Skills
    soft_skills = []
    for skill in ["leadership", "communication", "teamwork", "problem solving", "analytical"]:
        if skill in text:
            soft_skills.append(skill.title())

    # 6. Additional Fields
    location = None
    if "remote" in text: location = "Remote"
    elif "hybrid" in text: location = "Hybrid"
    
    employment_type = None
    if "full time" in text or "full-time" in text: employment_type = "Full-Time"
    elif "part time" in text or "part-time" in text: employment_type = "Part-Time"
    elif "contract" in text: employment_type = "Contract"
    
    salary_range = None
    salary_match = re.search(r'\$?(\d{2,3}k?)[-\sto]+\$?(\d{2,3}k)', text)
    if salary_match:
        salary_range = f"${salary_match.group(1)} - ${salary_match.group(2)}"
        
    tools = [s for s in required_skills if s.lower() in ["docker", "kubernetes", "git", "aws", "azure", "gcp"]]
    frameworks = [s for s in required_skills if s.lower() in ["react", "node.js", "django", "flask", "spring"]]
    
    return JobDescriptionData(
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience=experience_years,
        education=education,
        certifications=certifications,
        keywords=required_skills + soft_skills,
        tools=tools,
        frameworks=frameworks,
        technologies=required_skills,
        soft_skills=soft_skills,
        location=location,
        employment_type=employment_type,
        salary_range=salary_range
    )

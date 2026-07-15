from backend.models.response_models import ResumeData, JobDescriptionData, ResumeMatchData

def compute_resume_match(resume: ResumeData, jd: JobDescriptionData) -> ResumeMatchData:
    """
    Deterministically computes a match score between a parsed resume and a parsed job description.
    Weights: Skills 35%, Projects 15%, Keywords 15%, Experience 20%, Education 10%, Certification 5%.
    """
    
    resume_skills_lower = [s.lower() for s in resume.detected_skills]
    jd_skills_lower = [s.lower() for s in jd.required_skills]
    
    # 1. Skill Match (35%)
    matched_skills = [s for s in jd.required_skills if s.lower() in resume_skills_lower]
    missing_skills = [s for s in jd.required_skills if s.lower() not in resume_skills_lower]
    skill_score = (len(matched_skills) / len(jd_skills_lower) * 35) if jd_skills_lower else 35
        
    # 2. Keywords Match (15%)
    resume_text_blob = " ".join([d.get("detail", "").lower() for d in resume.experience] + 
                                [d.get("detail", "").lower() for d in resume.projects])
    resume_text_blob += " " + (resume.resume_summary or "").lower()
    
    matched_keywords = []
    missing_keywords = []
    for kw in jd.keywords:
        if kw.lower() in resume_text_blob or kw.lower() in resume_skills_lower:
            matched_keywords.append(kw)
        else:
            missing_keywords.append(kw)
            
    kw_score = (len(matched_keywords) / len(jd.keywords) * 15) if jd.keywords else 15
        
    # 3. Project Match (15%) -> evaluate overlap with JD technologies/frameworks
    project_text_blob = " ".join([d.get("detail", "").lower() for d in resume.projects])
    jd_tech = jd.technologies + jd.tools
    matched_tech_in_projects = [t for t in jd_tech if t.lower() in project_text_blob]
    
    project_score = 15
    project_gap = None
    if jd_tech:
        project_score = (len(matched_tech_in_projects) / len(jd_tech) * 15)
        if project_score < 7.5:
            project_gap = f"Projects lack mention of key JD tech: {', '.join(jd_tech[:3])}"
            
    # 4. Experience Match (20%)
    exp_gap = None
    exp_score = 20
    if jd.experience and not resume.experience:
        exp_gap = f"JD requires {jd.experience}, but no experience found."
        exp_score = 0
        
    # 5. Education Match (10%)
    edu_gap = None
    edu_score = 10
    if jd.education:
        edu_text = " ".join([d.get("detail", "").lower() for d in resume.education])
        req_ed = jd.education.lower()
        if "bachelor" in req_ed and "bachelor" not in edu_text and "b.tech" not in edu_text and "b.s" not in edu_text:
            edu_gap = "Missing Bachelor's degree."
            edu_score = 0
        elif "master" in req_ed and "master" not in edu_text and "m.s" not in edu_text and "m.tech" not in edu_text:
            edu_gap = "Missing Master's degree."
            edu_score = 0
            
    # 6. Certification Match (5%)
    cert_gap = None
    cert_score = 5
    if jd.certifications:
        missing_certs = [c for c in jd.certifications if c.lower() not in resume_text_blob]
        if missing_certs:
            cert_gap = f"Missing certifications: {', '.join(missing_certs)}"
            cert_score = 0
            
    overall_match = int(skill_score + kw_score + project_score + exp_score + edu_score + cert_score)
    
    # Priority improvements
    priority = []
    if exp_gap: priority.append("Gain relevant experience.")
    if project_gap: priority.append("Build projects using JD specific technologies.")
    if missing_skills: priority.append(f"Learn missing skills: {', '.join(missing_skills[:3])}")
    if cert_gap: priority.append("Acquire required certifications.")
    
    return ResumeMatchData(
        overall_match_score=overall_match,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        experience_gap=exp_gap,
        education_gap=edu_gap,
        certification_gap=cert_gap,
        project_gap=project_gap,
        ATS_score=resume.ats_score,
        improvement_priority=priority,
        recommended_courses=[],
        recommended_projects=[],
        gemini_suggestions=None
    )

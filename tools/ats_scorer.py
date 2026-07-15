from typing import Dict, Any, Tuple

def score_ats(parsed_resume: Dict[str, Any]) -> Tuple[int, list[str]]:
    """
    Deterministically scores ATS compliance based on structural elements.
    """
    score = 0
    missing = []
    
    if parsed_resume.get("detected_skills"):
        score += 30
    else:
        missing.append("No explicit skills section found")
        
    if parsed_resume.get("experience"):
        score += 40
    else:
        missing.append("No professional experience section found")
        
    if parsed_resume.get("education"):
        score += 20
    else:
        missing.append("No education section found")
        
    if parsed_resume.get("projects"):
        score += 10
    else:
        missing.append("No projects section found")
        
    return score, missing

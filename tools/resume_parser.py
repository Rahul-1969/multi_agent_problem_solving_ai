import re
from typing import Dict, Any

def parse_resume(raw_text: str) -> Dict[str, Any]:
    """
    Deterministically parses raw resume text into structural blocks.
    Supports basic heuristic extraction.
    """
    parsed = {
        "resume_summary": "",
        "detected_skills": [],
        "education": [],
        "experience": [],
        "projects": [],
    }
    
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return parsed
        
    # Heuristics for sections
    current_section = "resume_summary"
    for line in lines:
        lower_line = line.lower()
        if "education" in lower_line and len(line) < 20:
            current_section = "education"
        elif "experience" in lower_line and len(line) < 20:
            current_section = "experience"
        elif "skills" in lower_line and len(line) < 20:
            current_section = "detected_skills"
        elif "projects" in lower_line and len(line) < 20:
            current_section = "projects"
        elif "summary" in lower_line and len(line) < 20:
            current_section = "resume_summary"
        else:
            if current_section == "detected_skills":
                parsed["detected_skills"].extend([s.strip() for s in line.split(',') if s.strip()])
            elif current_section in ["education", "experience", "projects"]:
                parsed[current_section].append({"detail": line})
            elif current_section == "resume_summary":
                parsed["resume_summary"] += line + " "
                
    parsed["resume_summary"] = parsed["resume_summary"].strip()
    return parsed

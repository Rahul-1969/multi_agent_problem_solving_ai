def generate_strengths(meta: dict) -> list[str]:
    """Generates data-driven strengths."""
    strengths = []
    
    placements = meta.get("placement_percentage") or 0
    if placements >= 90:
        strengths.append("Excellent placement record")
    elif placements >= 80:
        strengths.append("Very good placements")
        
    avg_pkg = meta.get("avg_package_lpa") or 0
    if avg_pkg >= 8:
        strengths.append("High average package")
        
    if meta.get("autonomous"):
        strengths.append("Autonomous curriculum")
        
    naac = meta.get("naac_grade")
    if naac in ["A++", "A+"]:
        strengths.append(f"Highest NAAC Accreditation ({naac})")
        
    recruiters = meta.get("top_recruiters") or []
    if len(recruiters) >= 5:
        strengths.append("Strong recruiter network")
        
    nirf = meta.get("nirf_rank")
    if nirf and str(nirf).isdigit() and int(nirf) <= 200:
        strengths.append(f"Top {nirf} NIRF Ranked")
        
    return strengths

def generate_weaknesses(meta: dict) -> list[str]:
    """Generates data-driven weaknesses."""
    weaknesses = []
    
    fee = meta.get("tuition_fee_per_year") or 0
    if fee > 120000:
        weaknesses.append("High tuition fee")
        
    if not meta.get("hostel_available"):
        weaknesses.append("No on-campus hostel facility")
        
    naac = meta.get("naac_grade")
    if not naac or naac in ["N/A", "C", "B"]:
        weaknesses.append("Lower or missing NAAC accreditation")
        
    placements = meta.get("placement_percentage") or 0
    if placements > 0 and placements < 60:
        weaknesses.append("Below average placement record")
        
    return weaknesses

def generate_counselor_summary(meta: dict, user_data: dict) -> dict:
    """Generates the counselor counseling block."""
    branch = user_data.get("preferred_branch", "Engineering")
    
    why_choose = f"Consider this college if you are prioritizing a stable career path in {branch}. It offers a balanced academic environment with reliable corporate tie-ups."
    
    placements = meta.get("placement_percentage") or 0
    fee = meta.get("tuition_fee_per_year") or 0
    
    ideal_for = []
    if placements >= 80:
        ideal_for.append("Students seeking strong corporate placements")
    if meta.get("autonomous"):
        ideal_for.append("Students preferring an updated, flexible curriculum")
    if fee < 80000:
        ideal_for.append("Value-conscious students prioritizing ROI")
        
    if not ideal_for:
        ideal_for.append("Students looking for a standard engineering degree")
        
    not_recommended_if = []
    if fee > 130000:
        not_recommended_if.append("Budget is a strict constraint")
    if not meta.get("hostel_available"):
        not_recommended_if.append("On-campus hostel is required")
        
    return {
        "why_choose": why_choose,
        "ideal_for": " • ".join(ideal_for),
        "not_recommended_if": " • ".join(not_recommended_if) if not_recommended_if else "None",
        "career_opportunities": "Software Engineering, Core Engineering Roles, Higher Studies",
        "higher_studies_support": "Average to Good" if meta.get("autonomous") else "Standard"
    }

def generate_final_verdict(meta: dict, user_data: dict, admission_chance_pct: int) -> str:
    """Generates a concise <50 word final verdict."""
    placements = meta.get("placement_percentage") or 0
    fee = meta.get("tuition_fee_per_year") or 0
    
    verdict = "This college is "
    if placements >= 85 and admission_chance_pct >= 60:
        verdict += "an excellent option for your rank because it offers strong placements and a high probability of admission. "
    elif admission_chance_pct >= 60:
        verdict += "a safe option for your rank with decent opportunities. "
    else:
        verdict += "a competitive 'Dream' option. Admission is unlikely but worth trying in counseling. "
        
    if fee > 120000:
        verdict += "Keep the higher tuition fees in mind."
    else:
        verdict += "It provides very solid ROI."
        
    return verdict

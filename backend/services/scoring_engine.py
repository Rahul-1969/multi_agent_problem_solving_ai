def calculate_quality_score(meta: dict) -> float:
    """Computes a 0-100 quality score for a college."""
    score = 0
    if meta.get("autonomous"): score += 20
    
    naac = meta.get("naac_grade")
    if naac == "A++": score += 20
    elif naac == "A+": score += 18
    elif naac == "A": score += 15
    elif naac == "B++": score += 10
    elif naac == "B+": score += 8
    
    if meta.get("nba_accredited"): score += 10
    
    placements = meta.get("placement_percentage") or 0
    if placements >= 90: score += 15
    elif placements >= 80: score += 10
    elif placements >= 70: score += 5
    
    avg_pkg = meta.get("avg_package_lpa") or 0
    if avg_pkg >= 8: score += 15
    elif avg_pkg >= 6: score += 10
    elif avg_pkg >= 4: score += 5
    
    highest_pkg = meta.get("highest_package_lpa") or 0
    if highest_pkg >= 40: score += 5
    elif highest_pkg >= 20: score += 3
    
    nirf = meta.get("nirf_rank")
    if nirf and str(nirf).isdigit() and int(nirf) <= 200:
        score += 10
        
    top_recruiters = meta.get("top_recruiters") or []
    if len(top_recruiters) >= 5: score += 5
    
    return min(100.0, float(score))

def calculate_roi_score(meta: dict) -> tuple[float, str]:
    """Calculates ROI (0-100) and returns (score, label)."""
    placements = meta.get("placement_percentage") or 0
    avg_pkg = meta.get("avg_package_lpa") or 0
    highest_pkg = meta.get("highest_package_lpa") or 0
    fees = meta.get("tuition_fee_per_year") or 100000
    hostel = meta.get("hostel_fee") or 0
    
    # Very basic median approximation if none
    median_pkg = meta.get("median_package_lpa") or avg_pkg * 0.9
    
    total_cost_4yrs = ((fees + hostel) * 4) / 100000.0  # in LPA
    if total_cost_4yrs <= 0:
        total_cost_4yrs = 4.0
        
    roi_ratio = ((avg_pkg * 0.6) + (median_pkg * 0.3) + (highest_pkg * 0.1)) / total_cost_4yrs
    
    score = min(100.0, roi_ratio * 30.0 + (placements * 0.2))
    
    if score >= 80: label = "⭐⭐⭐⭐⭐ Excellent ROI"
    elif score >= 60: label = "⭐⭐⭐⭐ Good ROI"
    else: label = "⭐⭐⭐ Average ROI"
    
    return float(round(score, 1)), label

def calculate_student_match_score(meta: dict, user_data: dict, admission_chance_pct: int) -> float:
    """Calculates how well the college suits THIS student (0-100)."""
    score = admission_chance_pct * 0.4  # Up to 40 points for admission probability
    
    # Location match
    pref_loc = user_data.get("location")
    if pref_loc and meta.get("district") == pref_loc:
        score += 20
    elif not pref_loc:
        score += 15 # No preference, slight bump
        
    # Gender / Category reservation (if minority matches)
    category = user_data.get("category", "OC")
    if meta.get("minority_status") == "Muslim" and category == "Minority":
        score += 20
    elif meta.get("college_type") == "Women" and user_data.get("gender") == "female":
        score += 20
    elif meta.get("college_type") == "Women" and user_data.get("gender") == "male":
        score -= 50 # Invalid
        
    # Hostel requirement
    # Assume user requires hostel if they specify a distant location or it's implicitly true
    if meta.get("hostel_available"):
        score += 10
        
    return max(0.0, min(100.0, float(round(score, 1))))

def calculate_confidence(meta: dict, admission_chance_pct: int) -> str:
    """Calculates confidence score (High/Medium/Low)."""
    # 40% Metadata quality
    meta_score = 0
    if meta.get("avg_package_lpa"): meta_score += 10
    if meta.get("placement_percentage"): meta_score += 10
    if meta.get("tuition_fee_per_year"): meta_score += 10
    if meta.get("naac_grade"): meta_score += 10
    
    # 30% Branch Match (Assume 30% as base if predicted branches exist)
    branch_score = 30
    
    # 20% Admission Certainty
    adm_score = min(20, (admission_chance_pct / 100.0) * 20)
    
    # 10% Data Freshness (Assume 10 for now)
    fresh_score = 10
    
    total = meta_score + branch_score + adm_score + fresh_score
    if total >= 80: return "High"
    elif total >= 60: return "Medium"
    else: return "Low"

def calculate_campus_rating(meta: dict) -> int:
    """Returns a star rating (1-5) for Campus Life."""
    score = 2 # Base 2 stars
    if meta.get("campus_area_acres") and meta.get("campus_area_acres") > 20: score += 1
    if meta.get("hostel_available"): score += 1
    if meta.get("sports_facilities"): score += 0.5
    if meta.get("student_clubs"): score += 0.5
    if meta.get("transport_available"): score += 0.5
    return min(5, int(score))

def calculate_final_ranking(quality: float, admission_pct: int, popularity: float) -> dict:
    """Returns the total score and the breakdown explanation."""
    q_val = quality * 0.5
    a_val = admission_pct * 0.3
    p_val = popularity * 0.2
    total = q_val + a_val + p_val
    return {
        "overall": round(total, 1),
        "quality_contrib": round(q_val, 1),
        "admission_contrib": round(a_val, 1),
        "popularity_contrib": round(p_val, 1)
    }

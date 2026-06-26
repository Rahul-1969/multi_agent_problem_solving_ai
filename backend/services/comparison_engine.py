def build_comparison_payload(
    meta: dict,
    campus_rating: int,
    roi_score: float,
    match_score: float,
    quality_score: float
) -> dict:
    """Packages structured data so any two colleges can be compared instantly."""
    
    placements = meta.get("placement_percentage") or 0
    avg_pkg = meta.get("avg_package_lpa") or 0
    highest_pkg = meta.get("highest_package_lpa") or 0
    fee = meta.get("tuition_fee_per_year") or 0
    
    return {
        "academics": {
            "autonomous": meta.get("autonomous", False),
            "naac_grade": meta.get("naac_grade", "N/A"),
            "nba_accredited": meta.get("nba_accredited", False),
            "nirf_rank": meta.get("nirf_rank", "N/A"),
            "quality_score_100": round(quality_score, 1)
        },
        "placements": {
            "placement_percentage": placements,
            "average_package": avg_pkg,
            "highest_package": highest_pkg,
            "top_recruiters": meta.get("top_recruiters", [])
        },
        "roi": {
            "roi_score_100": roi_score,
            "tuition_fee": fee,
            "hostel_fee": meta.get("hostel_fee") or 0
        },
        "campus": {
            "campus_rating_stars": campus_rating,
            "campus_area_acres": meta.get("campus_area_acres"),
            "hostel_available": meta.get("hostel_available", False),
            "transport_available": meta.get("transport_available", False)
        },
        "affordability": {
            "total_cost_4_years": (fee + (meta.get("hostel_fee") or 0)) * 4
        },
        "recommendation": {
            "student_match_score_100": match_score
        }
    }

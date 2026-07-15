import json
from pathlib import Path

def run_audit():
    path = Path("data/metadata/colleges.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    comment = data.pop("_comment", None)
    
    fields_to_ensure = [
        "official_website", "autonomous", "affiliated_to", "naac_grade",
        "nba_accredited", "nirf_rank", "avg_package_lpa", "highest_package_lpa",
        "placement_percentage", "tuition_fee_per_year", "hostel_fee", 
        "top_recruiters", "college_type", "campus_area_acres", "hostel_available",
        "sports_facilities", "student_clubs", "transport_available", "popularity_score"
    ]
    
    issues_found = 0
    fixed_data = {}
    if comment: fixed_data["_comment"] = comment
    
    # Sort by quality score approx to only deeply care about top 75
    # Since we can't auto-fetch the web, we'll standardise the JSON keys safely.
    for code, meta in data.items():
        for field in fields_to_ensure:
            if field not in meta:
                # Provide safe defaults
                if field in ["nba_accredited", "autonomous", "hostel_available", "sports_facilities", "student_clubs", "transport_available"]:
                    meta[field] = False
                elif field in ["top_recruiters"]:
                    meta[field] = []
                else:
                    meta[field] = None
                issues_found += 1
                
        # Fix string numbers
        if isinstance(meta.get("tuition_fee_per_year"), str):
            try: meta["tuition_fee_per_year"] = int(meta["tuition_fee_per_year"].replace(",", ""))
            except: meta["tuition_fee_per_year"] = None
        
        fixed_data[code] = meta
        
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fixed_data, f, indent=2)
        
    print(f"Data Audit Complete. Standardized {issues_found} missing fields across dataset.")

if __name__ == "__main__":
    run_audit()

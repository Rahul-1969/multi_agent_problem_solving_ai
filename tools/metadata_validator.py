import json
from pathlib import Path

def validate():
    path = Path("data/college_metadata.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data.pop("_comment", None)
    
    issues = []
    
    for code, meta in data.items():
        name = meta.get("display_name", code)
        
        # Check website
        website = meta.get("official_website")
        if not website:
            issues.append(f"[{code}] {name}: Missing official website")
        elif not (website.startswith("http://") or website.startswith("https://")):
            issues.append(f"[{code}] {name}: Invalid website URL (must start with http)")
            
        # Check NAAC
        naac = meta.get("naac_grade")
        if not naac or naac == "N/A":
            issues.append(f"[{code}] {name}: Missing NAAC grade")
            
        # Check placements
        p = meta.get("placement_percentage")
        if p is not None and (p < 0 or p > 100):
            issues.append(f"[{code}] {name}: Invalid placement percentage ({p})")
            
        # Check packages
        avg = meta.get("avg_package_lpa")
        high = meta.get("highest_package_lpa")
        if avg is not None and (avg < 1 or avg > 50):
            issues.append(f"[{code}] {name}: Suspicious average package ({avg})")
        if high is not None and avg is not None and high < avg:
            issues.append(f"[{code}] {name}: Highest package ({high}) is lower than average ({avg})")
            
        # Check logo
        if not meta.get("college_image_url"):
            issues.append(f"[{code}] {name}: Missing logo URL")

    if issues:
        print(f"Metadata Validation Failed. Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Metadata Validation Passed! All checks OK.")

if __name__ == "__main__":
    validate()

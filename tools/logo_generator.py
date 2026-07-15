import json
import re
from pathlib import Path

def extract_domain(url):
    if not url: return None
    # Remove http://, https://, www.
    url = re.sub(r'^https?:\/\/', '', url)
    url = re.sub(r'^www\.', '', url)
    # Get just the domain (before any slash)
    domain = url.split('/')[0]
    return domain.strip()

def run():
    path = Path("data/metadata/colleges.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    comment = data.pop("_comment", None)
    
    for code, meta in data.items():
        website = meta.get("official_website")
        if website:
            domain = extract_domain(website)
            if domain:
                meta["college_image_url"] = f"https://logo.clearbit.com/{domain}"
            else:
                meta["college_image_url"] = None
        else:
            meta["college_image_url"] = None
            
    out_data = {}
    if comment: out_data["_comment"] = comment
    out_data.update(data)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

if __name__ == "__main__":
    run()
    print("Logo URLs generated successfully.")

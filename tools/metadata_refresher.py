import json
import os
import shutil
import argparse
from pathlib import Path
from backend.providers.provider_factory import get_provider
from tools.knowledge_refresh_engine import refresh_engine
from tools.metadata_loader import load_college_metadata
from utils.logger import get_logger

logger = get_logger(__name__)

def run_refresh(colleges: list[str] = None, dry_run: bool = False):
    """
    Fetches fresh data, validates, diffs, and prompts for approval.
    """
    provider = get_provider("enrich")
    metadata = load_college_metadata()
    data_dir = Path(__file__).parent.parent / "data" / "metadata"
    
    if not colleges:
        colleges = list(metadata.keys())[:3]
        
    print(f"Starting metadata refresh for: {', '.join(colleges)}")
    if dry_run:
        print("[DRY-RUN MODE] No changes will be saved.")
    
    try:
        enriched_data = provider.enrich_batch(colleges)
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    updates_to_apply = {}
    
    for code in colleges:
        if code not in enriched_data:
            print(f"No new data returned for {code}")
            continue
            
        old_data = metadata.get(code, {})
        new_data = enriched_data[code]
        
        is_valid, reason = refresh_engine.validate_metadata(old_data, new_data)
        if not is_valid:
            print(f"[{code}] Validation REJECTED: {reason}")
            refresh_engine.log_rejected(data_dir, code, reason, old_data, new_data)
            continue
            
        diff = refresh_engine.generate_diff(old_data, new_data)
        if diff.strip() == "No changes":
            print(f"[{code}] No changes detected.")
            continue
            
        print(f"\n[{code}] Proposed Changes:")
        print(diff)
        
        if dry_run:
            continue
            
        ans = input(f"Approve changes for {code}? (y/n/a[all]): ").strip().lower()
        if ans == 'y':
            updates_to_apply[code] = new_data
        elif ans == 'a':
            updates_to_apply[code] = new_data
        else:
            print(f"Changes for {code} rejected by user.")
            
    if updates_to_apply and not dry_run:
        print(f"\nApplying approved updates for {len(updates_to_apply)} colleges...")
        refresh_engine.approve_and_save(data_dir, metadata, updates_to_apply)
        print("Saved to disk.")
        
        # Trigger FastAPI reload
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:8000/admin/metadata/reload", method="POST")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print("Successfully triggered FastAPI in-memory metadata reload.")
                else:
                    print(f"FastAPI reload returned status: {response.status}")
        except Exception as e:
            print(f"Warning: Could not trigger FastAPI metadata reload (is the server running?): {e}")
            
        print("Done.")
    else:
        print("\nNo updates applied.")

def run_rollback(version: int):
    data_dir = Path(__file__).parent.parent / "data" / "metadata"
    target_v = data_dir / "versions" / f"v{version}.json"
    if not target_v.exists():
        print(f"Version {version} not found at {target_v}")
        return
    main_file = data_dir / "colleges.json"
    shutil.copy2(target_v, main_file)
    print(f"Rolled back colleges.json to version {version}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh College Metadata")
    parser.add_argument("--colleges", type=str, help="Comma-separated list of college codes to refresh")
    parser.add_argument("--dry-run", action="store_true", help="Run without saving")
    parser.add_argument("--rollback", type=int, help="Rollback to a specific version number")
    args = parser.parse_args()
    
    if args.rollback is not None:
        run_rollback(args.rollback)
    else:
        colleges = args.colleges.split(",") if args.colleges else None
        run_refresh(colleges, args.dry_run)

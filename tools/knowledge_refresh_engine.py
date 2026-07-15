import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)

class ValidationError(Exception):
    pass

class KnowledgeRefreshEngine:
    def __init__(self):
        pass

    def validate_metadata(self, old: Dict[str, Any], new: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates the candidate metadata against the old one.
        Returns (is_valid, reason).
        """
        try:
            # Check package consistency
            old_pkg = old.get("highest_package_lpa")
            new_pkg = new.get("highest_package_lpa")
            if old_pkg is not None and new_pkg is not None:
                # Reject anomalous package increases without manual review
                if new_pkg > old_pkg * 1.4:
                    return False, f"highest_package_lpa jumped by >40% from {old_pkg} to {new_pkg}"

            # Check NAAC grade
            naac_grade = new.get("naac_grade")
            if naac_grade and naac_grade not in ["A++", "A+", "A", "B++", "B+", "B", "C", "N/A"]:
                return False, f"Invalid NAAC grade: {naac_grade}"
                
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {e}"

    def generate_diff(self, old: Dict[str, Any], new: Dict[str, Any]) -> str:
        """
        Generate a human-readable diff.
        """
        diff_lines = []
        all_keys = set(old.keys()).union(set(new.keys()))
        for key in sorted(all_keys):
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                diff_lines.append(f"  {key}: {old_val} -> {new_val}")
        return "\n".join(diff_lines) if diff_lines else "  No changes"

    def log_rejected(self, data_dir: Path, code: str, reason: str, old: dict, new: dict):
        logs_dir = data_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        changes_file = logs_dir / "changes.json"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "status": "REJECTED",
            "reason": reason,
            "old": old,
            "new": new
        }
        
        logs = []
        if changes_file.exists():
            with open(changes_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append(entry)
        with open(changes_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

    def approve_and_save(self, data_dir: Path, current_metadata: Dict[str, Any], updates: Dict[str, Any], target_filename: str = "colleges.json"):
        """
        Versioning and saving.
        """
        metadata_file = data_dir / target_filename
        versions_dir = data_dir / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine next version
        version = 1
        while (versions_dir / f"v{version}.json").exists():
            version += 1
            
        backup_file = versions_dir / f"v{version}.json"
        
        # Save backup
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(old_data, f, indent=4)
            logger.info(f"Backed up current metadata to {backup_file.name}")
            
        # Log approved changes
        logs_dir = data_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        changes_file = logs_dir / "changes.json"
        logs = []
        if changes_file.exists():
            with open(changes_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
                
        # Apply updates
        for code, new_data in updates.items():
            entry = {
                "timestamp": datetime.now().isoformat(),
                "code": code,
                "status": "APPROVED",
                "diff": self.generate_diff(current_metadata.get(code, {}), new_data)
            }
            logs.append(entry)
            
            if code not in current_metadata:
                current_metadata[code] = {}
            current_metadata[code].update(new_data)
            
        with open(changes_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)
            
        # Save new
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(current_metadata, f, indent=4)
        logger.info(f"Saved new metadata to {metadata_file.name}")

refresh_engine = KnowledgeRefreshEngine()

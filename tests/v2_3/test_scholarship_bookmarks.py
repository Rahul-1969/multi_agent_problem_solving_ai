import pytest
from backend.auth.user_store import user_store
from backend.services.scholarship_engine import evaluate_bookmarked_scholarships
from tools.metadata_loader import _SCHOLARSHIP_METADATA_PATH as SCHOLARSHIPS_JSON_PATH, load_scholarship_metadata
import json
import os
from unittest.mock import patch
from backend.models.response_models import ScholarshipItem

def test_scholarship_bookmarks():
    # Write a temporary dummy scholarship
    dummy_data = {
        "DUMMY_123": {
            "scholarship_name": "Test Scholarship",
            "provider": "Test",
            "income_limit": 500000,
            "category": "Minority"
        }
    }
    
    # Backup original
    original = {}
    if os.path.exists(SCHOLARSHIPS_JSON_PATH):
        with open(SCHOLARSHIPS_JSON_PATH, 'r', encoding='utf-8') as f:
            original = json.load(f)
            
    try:
        with open(SCHOLARSHIPS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f)
            
        load_scholarship_metadata(force_reload=True)
            
        # Test evaluation logic
        with patch('backend.services.scholarship_engine.enrich_scholarships') as mock_enrich:
            mock_enrich.side_effect = lambda matches, p: [
                ScholarshipItem(
                    scholarship_name=m["scholarship_name"],
                    provider=m["provider"],
                    eligibility="N/A",
                    amount="TBD",
                    deadline="TBD",
                    match_score=m["match_score"],
                    eligibility_status=m.get("eligibility_status")
                ) for m in matches
            ]
            
            # Eligible profile
            profile1 = {"income": 400000, "category": "Minority"}
            res1 = evaluate_bookmarked_scholarships(["DUMMY_123"], profile1)
            assert len(res1.scholarships) == 1
            assert res1.scholarships[0].match_score == 100.0
            
            # Ineligible profile (Income too high)
            profile2 = {"income": 600000, "category": "Minority"}
            res2 = evaluate_bookmarked_scholarships(["DUMMY_123"], profile2)
            assert len(res2.scholarships) == 1
            assert res2.scholarships[0].match_score == 50.0 # because Nearly Eligible (1 of 2 criteria met)
        
    finally:
        # Restore
        with open(SCHOLARSHIPS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(original, f)
            
        load_scholarship_metadata(force_reload=True)

import pytest
from backend.services.scholarship_engine import match_scholarships
from backend.models.user_models import ProfileData

def test_match_scholarships_deterministic():
    # Test income limit
    profile_rich = ProfileData(income=900000)
    matches_rich = match_scholarships(profile_rich)
    # AI_SCHOLAR_01 (8L), MERIT_02 (2L), STATE_04 (5L), WOMEN_05 (10L), SC_ST_06 (6L), BC_07 (2.5L), EWS_08 (8L), DISABILITY_09 (2.5L)
    # Should only get Women in Tech (10L limit) if gender is any/female
    # Wait, Women_05 requires Female gender.
    
    profile_eligible = ProfileData(income=100000, gender="Female", category="SC", state="Telangana", disability=True)
    matches = match_scholarships(profile_eligible)
    assert len(matches) > 0
    # Should get almost all of them since income is 1L. 
    # Let's verify filtering
    assert all(m.get("income_limit") >= 100000 for m in matches)

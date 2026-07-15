import pytest
from backend.services.export_service import export_service
from backend.models.response_models import ResumeMatchData

def test_export_pdf():
    data = ResumeMatchData(
        overall_match_score=85,
        matched_skills=["Python", "React"],
        missing_skills=["AWS"],
        experience_gap="None",
        gemini_suggestions="Great resume."
    )
    
    pdf_bytes = export_service.export("Test Report", data, "resume_match")
    
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

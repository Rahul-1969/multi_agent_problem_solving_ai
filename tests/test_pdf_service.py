from backend.services.pdf_service import answer_from_pdf, clear_pdf
from tools.pdf_session_store import DEFAULT_SESSION_ID, pdf_session_store


def test_answer_from_pdf_returns_error_when_pdf_not_loaded(monkeypatch):
    monkeypatch.setattr(pdf_session_store, 'is_loaded', lambda session_id: False)
    result = answer_from_pdf("What is this?", DEFAULT_SESSION_ID)

    assert result["success"] is False
    assert "No PDF loaded" in result["response"]


def test_clear_pdf_returns_no_pdf_when_none_loaded(monkeypatch):
    monkeypatch.setattr(pdf_session_store, 'status', lambda session_id: {"loaded": False})
    result = clear_pdf(DEFAULT_SESSION_ID)

    assert result["success"] is False
    assert "No PDF" in result["message"]

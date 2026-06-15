"""
backend/services/pdf_service.py
Service layer for PDF load/query/status operations.
"""

from utils.logger import get_logger
import os
from tools.pdf_session_manager import DEFAULT_SESSION_ID, pdf_session_manager
from pipelines.pdf_pipeline import pdf_pipeline

logger = get_logger(__name__)


def load_pdf(file_path: str, session_id: str | None = None) -> dict:
    """Load a PDF from disk for a specific PDF session."""
    session_id = session_id or pdf_session_manager.create_session_id()
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}
    try:
        info = pdf_session_manager.load(session_id, file_path)
        return {
            "success":  True,
            "session_id": session_id,
            "filename": info["filename"],
            "pages":    info["pages"],
            "chunks":   info["chunks"],
            "message":  "PDF loaded successfully",
        }
    except Exception:
        logger.exception("PDF load failed: %s", file_path)
        raise


def get_pdf_status(session_id: str | None = None) -> dict:
    """Return current PDF load status for a given session."""
    session_id = session_id or DEFAULT_SESSION_ID
    return pdf_session_manager.status(session_id)


def clear_pdf(session_id: str | None = None) -> dict:
    """Unload the current PDF for a given session."""
    session_id = session_id or DEFAULT_SESSION_ID
    status = pdf_session_manager.status(session_id)
    if status["loaded"]:
        name = status["filename"]
        pdf_session_manager.clear(session_id)
        return {"success": True, "session_id": session_id, "message": f"PDF '{name}' unloaded"}
    return {"success": False, "session_id": session_id, "message": "No PDF is currently loaded"}


def answer_from_pdf(question: str, session_id: str | None = None) -> dict:
    """Answer a question from the loaded PDF for a given session."""
    session_id = session_id or DEFAULT_SESSION_ID
    if not pdf_session_manager.is_loaded(session_id):
        return {"success": False, "response": "No PDF loaded. Use /pdf/load first.", "session_id": session_id}
    store = pdf_session_manager.get_store(session_id)
    response = pdf_pipeline(question, store.chunks, store.filename)
    return {"success": True, "session_id": session_id, "response": response}

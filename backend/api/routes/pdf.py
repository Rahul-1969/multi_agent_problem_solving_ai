"""
backend/api/routes/pdf.py
PDF management and Q&A endpoints.
"""

import os
from fastapi import APIRouter, Depends, UploadFile, File, Form
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.models.pdf_models import (
    PDFLoadRequest,
    PDFQuestionRequest,
    PDFLoadResponse,
    PDFStatusResponse,
    PDFAnswerResponse,
)
from backend.services.pdf_service import (
    answer_from_pdf,
    clear_pdf,
    get_pdf_status,
    load_pdf,
)
from config import UPLOAD_DIR
from tools.pdf_session_manager import pdf_session_manager
from utils.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)


def _resolve_session_id(session_id: str | None, current_user: TokenPayload) -> str:
    return session_id.strip() if session_id and session_id.strip() else current_user.username


@router.post("/pdf/load", response_model=PDFLoadResponse, summary="Load a PDF by path")
def load_pdf_by_path(
    request: PDFLoadRequest,
    current_user: TokenPayload = Depends(get_current_user),
) -> PDFLoadResponse:
    """
    Load a PDF from a server-side path.
    Body: {"path": "C:/path/to/file.pdf"}
    """
    path = request.path.strip()
    session_id = _resolve_session_id(request.session_id, current_user)
    if not path:
        return PDFLoadResponse(
            success=False,
            session_id=session_id,
            message="Missing 'path' field",
            error="No path provided",
        )

    # Prevent path traversal: resolve the requested path and ensure it stays
    # within the allowed UPLOAD_DIR.
    resolved_path = os.path.abspath(os.path.join(UPLOAD_DIR, path))
    if os.path.commonpath([os.path.abspath(UPLOAD_DIR), resolved_path]) != os.path.abspath(UPLOAD_DIR):
        return PDFLoadResponse(
            success=False,
            session_id=session_id,
            message="Invalid path",
            error="Path traversal is not allowed",
        )

    try:
        result = load_pdf(path, session_id)
    except Exception:
        logger.exception("Failed to load PDF from path: %s", path)
        raise

    return PDFLoadResponse(
        success=result["success"],
        session_id=session_id,
        filename=result.get("filename"),
        pages=result.get("pages"),
        chunks=result.get("chunks"),
        message=result.get("message", ""),
        error=result.get("error"),
    )


@router.post("/pdf/upload", response_model=PDFLoadResponse, summary="Upload a PDF file")
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
    current_user: TokenPayload = Depends(get_current_user),
) -> PDFLoadResponse:
    """
    Upload a PDF file directly. Saves to server and loads it.
    """
    session_id = _resolve_session_id(session_id, current_user)
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return PDFLoadResponse(
            success=False,
            session_id=session_id,
            message="Only PDF files allowed",
            error="Invalid file type",
        )

    safe_filename = os.path.basename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, safe_filename)
    if not safe_filename or os.path.commonpath([os.path.abspath(UPLOAD_DIR), os.path.abspath(save_path)]) != os.path.abspath(UPLOAD_DIR):
        return PDFLoadResponse(
            success=False,
            session_id=session_id,
            message="Invalid filename",
            error="Filename contains path traversal characters",
        )
    try:
        with open(save_path, "wb") as file_obj:
            content = await file.read()
            file_obj.write(content)

        result = load_pdf(save_path, session_id)
        return PDFLoadResponse(
            success=result["success"],
            session_id=session_id,
            filename=result.get("filename"),
            pages=result.get("pages"),
            chunks=result.get("chunks"),
            message=result.get("message", ""),
            error=result.get("error"),
        )
    except Exception:
        logger.exception("Failed to upload PDF: %s", getattr(file, "filename", "<unknown>"))
        raise


@router.get("/pdf/status", response_model=PDFStatusResponse, summary="Check loaded PDF status")
def pdf_status(
    session_id: str | None = None,
    current_user: TokenPayload = Depends(get_current_user),
) -> PDFStatusResponse:
    """Returns info about the currently loaded PDF."""
    session_id = _resolve_session_id(session_id, current_user)
    return PDFStatusResponse(**get_pdf_status(session_id))


@router.delete("/pdf/clear", summary="Unload the current PDF")
def clear(
    session_id: str | None = None,
    current_user: TokenPayload = Depends(get_current_user),
) -> dict[str, str]:
    """Unload the currently loaded PDF from memory."""
    session_id = _resolve_session_id(session_id, current_user)
    return clear_pdf(session_id)


@router.post("/pdf/ask", response_model=PDFAnswerResponse, summary="Ask a question from the PDF")
def ask_pdf(request: PDFQuestionRequest, current_user: TokenPayload = Depends(get_current_user)) -> PDFAnswerResponse:
    """
    Answer a question based on the currently loaded PDF.
    Must call /pdf/load or /pdf/upload first.
    """
    session_id = _resolve_session_id(request.session_id, current_user)
    result = answer_from_pdf(request.message, session_id)
    return PDFAnswerResponse(**result)

"""
backend/api/routes/knowledge.py

FastAPI router for RAG knowledge base management.
"""

import os
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, ConfigDict

from utils.logger import get_logger
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload

from backend.rag.ingestion_service import get_ingestion_service
from backend.rag.retriever import get_retriever

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge"])

# --- Pydantic Models ---
class IngestionResultModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    success: bool
    doc_id: Optional[str] = None
    chunks_stored: int = 0
    error: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[dict]

class KnowledgeQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    doc_types: Optional[List[str]] = None

class RetrievedChunkModel(BaseModel):
    text: str
    doc_name: str
    doc_type: str
    score: float

class KnowledgeQueryResponse(BaseModel):
    chunks: List[RetrievedChunkModel]

# --- Endpoints ---

ALLOWED_DOC_TYPES = {"syllabus", "placement", "college_faq", "resume", "scholarship", "interview_notes", "general"}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

@router.post("/upload", response_model=IngestionResultModel, summary="Upload a document for RAG ingestion")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("general"),
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Upload a document to the user's RAG knowledge base.
    """
    if doc_type not in ALLOWED_DOC_TYPES:
        doc_type = "general"

    # Validate file extension
    filename = file.filename or "unknown.txt"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension {ext}. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Stream to tempfile and validate size
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    try:
        size = 0
        with os.fdopen(fd, 'wb') as f:
            while chunk := await file.read(8192):
                size += len(chunk)
                if size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds the 20MB limit."
                    )
                f.write(chunk)
                
        # Call ingestion service
        ingestion_service = get_ingestion_service()
        # IngestionService.ingest returns IngestionResult
        result = ingestion_service.ingest(
            user_id=current_user.username,
            file_path=temp_path,
            doc_name=filename,
            doc_type=doc_type
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.error or "Ingestion failed"
            )
            
        return IngestionResultModel(
            success=result.success,
            doc_id=getattr(result, "doc_id", None),
            chunks_stored=getattr(result, "chunks_stored", 0),
            error=getattr(result, "error", None)
        )
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/list", response_model=DocumentListResponse, summary="List user's RAG documents")
def list_documents(current_user: TokenPayload = Depends(get_current_user)):
    """
    List all documents currently ingested in the user's knowledge base.
    """
    ingestion_service = get_ingestion_service()
    docs = ingestion_service.list_documents(current_user.username)
    return DocumentListResponse(documents=docs)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a RAG document")
def delete_document(doc_id: str, current_user: TokenPayload = Depends(get_current_user)):
    """
    Delete a document from the user's knowledge base. Idempotent.
    """
    ingestion_service = get_ingestion_service()
    ingestion_service.delete_document(current_user.username, doc_id)
    return None


@router.post("/query", response_model=KnowledgeQueryResponse, summary="Directly query the vector store")
def query_knowledge(
    request: KnowledgeQueryRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Query the vector store directly without going through the full LLM pipeline.
    This endpoint exists primarily for testing/debugging retrieval quality.
    """
    retriever = get_retriever()
    chunks = retriever.retrieve(
        user_id=current_user.username,
        query=request.query,
        top_k=request.top_k,
        doc_types=request.doc_types
    )
    
    response_chunks = [
        RetrievedChunkModel(
            text=c.text,
            doc_name=c.doc_name,
            doc_type=c.doc_type,
            score=c.score
        )
        for c in chunks
    ]
    return KnowledgeQueryResponse(chunks=response_chunks)

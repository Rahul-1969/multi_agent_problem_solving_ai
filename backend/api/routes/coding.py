"""
backend/api/routes/coding.py
Dedicated coding endpoint.
"""

from fastapi import APIRouter, Depends
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.models.request_models  import CodingRequest
from backend.models.response_models import ChatResponse
from backend.services.chatbot_service import process_query

router = APIRouter()


@router.post("/coding", response_model=ChatResponse, summary="Ask a coding question")
def coding(request: CodingRequest, current_user: TokenPayload = Depends(get_current_user)):
    """Direct coding queries — code generation, debugging, algorithms."""
    result: ChatResponse = process_query(request.message)
    return result

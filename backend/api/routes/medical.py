"""
backend/api/routes/medical.py
Dedicated medical endpoint.
"""

from fastapi import APIRouter, Depends
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.models.request_models  import MedicalRequest
from backend.models.response_models import ChatResponse
from backend.services.chatbot_service import process_query

router = APIRouter()


@router.post("/medical", response_model=ChatResponse, summary="Ask a medical question")
def medical(request: MedicalRequest, current_user: TokenPayload = Depends(get_current_user)):
    """Direct medical queries — symptoms, conditions, lifestyle advice."""
    result: ChatResponse = process_query(request.message)
    return result

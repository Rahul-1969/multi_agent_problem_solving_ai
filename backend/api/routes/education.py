"""
backend/api/routes/education.py
Dedicated education endpoint — always routes to education pipeline.
"""

from fastapi import APIRouter, Depends
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.models.request_models  import EducationRequest
from backend.models.response_models import ChatResponse
from backend.services.chatbot_service import process_query

router = APIRouter()


@router.post("/education", response_model=ChatResponse, summary="Ask an education question")
def education(request: EducationRequest, current_user: TokenPayload = Depends(get_current_user)):
    """
    Direct education queries without domain routing.
    Best for CS/IT concepts, OS, DBMS, networking, etc.
    """
    result: ChatResponse = process_query(request.message)
    return result

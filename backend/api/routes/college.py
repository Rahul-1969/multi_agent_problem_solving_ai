"""
backend/api/routes/college.py
Dedicated college prediction endpoint.
"""

import asyncio
from fastapi import APIRouter, Depends
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.models.request_models  import CollegeRequest
from backend.models.response_models import ChatResponse
from backend.services.chatbot_service import process_query

router = APIRouter()


@router.post("/college", response_model=ChatResponse, summary="Predict EAMCET colleges")
async def college(request: CollegeRequest, current_user: TokenPayload = Depends(get_current_user)):
    """
    EAMCET college prediction.
    Example input: "rank 5000 OC male CSE Hyderabad"
    """
    result: ChatResponse = await asyncio.to_thread(process_query, request.message)
    return result

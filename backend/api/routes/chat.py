"""
backend/api/routes/chat.py
Unified chat endpoint plus chat history routes for authenticated users.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from backend.models.request_models import ChatRequest, ChatCreateRequest, ChatMessageRequest
from backend.models.response_models import ChatResponse, ChatDetailResponse, ChatListResponse
from constants.domains import GENERAL_DOMAIN
from backend.services.chatbot_service import process_query
from backend.services.chat_history import chat_history_manager
from backend.services.streaming_service import create_text_streaming_response
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _format_chat_detail(chat: dict) -> dict:
    detail = {k: v for k, v in chat.items() if k != "id"}
    detail["chat_id"] = chat["id"]
    return detail


@router.get("/chats", response_model=ChatListResponse, summary="List chats")
def list_chats(current_user: TokenPayload = Depends(get_current_user)):
    return {"success": True, "chats": chat_history_manager.list_chats(current_user.username)}


@router.post("/chats", response_model=ChatDetailResponse, summary="Create a new chat")
def create_chat(request: ChatCreateRequest, current_user: TokenPayload = Depends(get_current_user)):
    chat = chat_history_manager.create_chat(current_user.username, request.title)
    return {"success": True, **_format_chat_detail(chat)}


@router.get("/chats/{chat_id}", response_model=ChatDetailResponse, summary="Get a chat by ID")
def get_chat(chat_id: str, current_user: TokenPayload = Depends(get_current_user)):
    chat = chat_history_manager.get_chat(current_user.username, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return {"success": True, **_format_chat_detail(chat)}


@router.delete("/chats/{chat_id}", summary="Delete a chat")
def delete_chat(chat_id: str, current_user: TokenPayload = Depends(get_current_user)):
    deleted = chat_history_manager.delete_chat(current_user.username, chat_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return {"success": True, "message": "Chat deleted"}


@router.post("/chats/{chat_id}/messages", response_model=ChatDetailResponse, summary="Append a message to a chat")
def append_chat_message(chat_id: str, request: ChatMessageRequest, current_user: TokenPayload = Depends(get_current_user)):
    if not request.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message content is required")
    chat = chat_history_manager.append_message(
        current_user.username,
        chat_id,
        {
            "sender": request.sender,
            "content": request.content,
            "domain": request.domain,
            "data": request.data,
            "created_at": None,
        },
    )
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return {"success": True, **_format_chat_detail(chat)}


@router.post("/chat", response_model=ChatResponse, summary="Send a query to the chatbot")
async def chat(request: ChatRequest, current_user: TokenPayload = Depends(get_current_user)):
    """
    Auto-routed endpoint. Returns:
    - domain: which pipeline handled the query
    - data:   structured domain-specific fields (code, conditions, colleges, etc.)
    - response: formatted string for direct display
    """
    if request.chat_id:
        chat = chat_history_manager.get_chat(current_user.username, request.chat_id)
        if chat is None:
            return ChatResponse(
                success=False,
                domain=GENERAL_DOMAIN,
                response="",
                error="Chat not found",
                chat_id=request.chat_id,
            )
        chat_history_manager.append_message(
            current_user.username,
            request.chat_id,
            {
                "sender": "user",
                "content": request.message,
                "domain": "user",
                "data": None,
                "created_at": None,
            },
        )

    is_first = True
    chat_history = None

    if request.chat_id:
        chat = chat_history_manager.get_chat(current_user.username, request.chat_id)
        if chat:
            chat_history = chat.get("messages", [])
            # It's the first message if history is empty before we append
            is_first = len(chat_history) == 0

    result = await asyncio.to_thread(
        process_query, 
        message=request.message,
        username=current_user.username,
        chat_id=request.chat_id,
        is_first_message=is_first,
        chat_history=chat_history
    )

    if request.chat_id:
        chat_history_manager.append_message(
            current_user.username,
            request.chat_id,
            {
                "sender": "bot",
                "content": result.response,
                "domain": result.domain,
                "data": result.data,
                "created_at": None,
            },
        )

    messages = None
    if request.chat_id:
        chat = chat_history_manager.get_chat(current_user.username, request.chat_id)
        messages = chat.get("messages") if chat else None

    return ChatResponse(
        success=result.success,
        domain=result.domain,
        data=result.data,
        response=result.response,
        messages=messages,
        chat_id=request.chat_id,
        error=result.error,
    )


@router.post("/chat/stream", summary="Send a query and receive a streaming text response")
async def chat_stream(request: ChatRequest, current_user: TokenPayload = Depends(get_current_user)):
    """
    Streaming endpoint.

    The current implementation generates the full response via the
    pipeline and then chunks it. True LLM-native streaming is
    available via ``llm.ollama_client.stream_llm`` but requires
    each pipeline to yield tokens instead of returning strings.
    """
    result = await asyncio.to_thread(process_query, request.message)
    # Prefix the stream with the domain so the UI can show the
    # active pipeline indicator immediately.
    domain_prefix = f"DOMAIN:{result.domain}\n"
    return create_text_streaming_response(domain_prefix + result.response)

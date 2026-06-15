"""
backend/models/request_models.py
Pydantic request models for all API endpoints.
"""

from typing import Any

from pydantic import BaseModel, Field, EmailStr


class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query")


class ChatRequest(MessageRequest):
    chat_id: str | None = Field(
        default=None,
        description="Optional chat ID for history tracking",
    )


class ChatCreateRequest(BaseModel):
    title: str | None = Field(
        default="New chat",
        max_length=100,
        description="Optional chat title",
    )


class ChatMessageRequest(BaseModel):
    sender: str = Field(..., min_length=1, description="Message sender")
    content: str = Field(..., min_length=1, description="Message content")
    domain: str | None = Field(default=None, description="Optional domain tag")
    data: dict[str, Any] | None = Field(default=None, description="Optional structured payload")


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Username for login")
    password: str = Field(..., min_length=1, description="Password for login")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=72, description="Password (6-72 characters)")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, description="Refresh token")


class CollegeRequest(MessageRequest):
    pass


class MedicalRequest(MessageRequest):
    pass


class EducationRequest(MessageRequest):
    pass


class CodingRequest(MessageRequest):
    pass

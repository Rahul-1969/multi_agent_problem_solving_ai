"""
backend/models/response_models.py
Structured Pydantic response models.

Every domain returns a typed 'data' dict instead of a raw string.
The raw formatted string is also included as 'response' for
backward compatibility with clients that already use it.
"""

from typing import Any, Final, Literal, TypeAlias

from constants.domains import (
    COLLEGE_DOMAIN,
    MEDICAL_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
)
from pydantic import BaseModel, Field, ConfigDict, model_validator


# Module constants and type aliases
MEDICAL_DISCLAIMER: Final[str] = (
    "This is AI-generated information only, NOT medical advice."
)

MODEL_CONFIG: Final = ConfigDict(extra="forbid")

DomainType = Literal[
    COLLEGE_DOMAIN,
    MEDICAL_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
]

# Domain-specific models


class EducationData(BaseModel):
    model_config = MODEL_CONFIG

    topic: str
    definition: str | None = None
    key_points: str | None = None
    example: str | None = None
    exam_tip: str | None = None


class MedicalData(BaseModel):
    model_config = MODEL_CONFIG

    conditions: str | None = None
    treatments: str | None = None
    lifestyle: str | None = None
    emergency: str | None = None
    disclaimer: str = MEDICAL_DISCLAIMER


class CodingData(BaseModel):
    model_config = MODEL_CONFIG

    language: str | None = None
    code: str | None = None
    explanation: str | None = None
    complexity: str | None = None
    clarification: list[str] | None = None


class CollegeData(BaseModel):
    model_config = MODEL_CONFIG

    rank: int | None = None
    category: str | None = None
    gender: str | None = None
    branch: str | None = None
    location: str | None = None
    safe: list[str] = Field(default_factory=list)
    moderate: list[str] = Field(default_factory=list)
    dream: list[str] = Field(default_factory=list)


class GeneralData(BaseModel):
    model_config = MODEL_CONFIG

    answer: str


# Unified response models


# Precise response data union
ResponseData: TypeAlias = (
    EducationData
    | MedicalData
    | CodingData
    | CollegeData
    | GeneralData
)

class BaseResponse(BaseModel):
    model_config = MODEL_CONFIG

    success: bool
    error: str | None = None


class ChatMessage(BaseModel):
    model_config = MODEL_CONFIG

    sender: str
    content: str
    text: str | None = None
    domain: str | None = None
    data: dict[str, Any] | None = None
    created_at: str | None = None

    @model_validator(mode="before")
    def _fill_text(cls, data):
        if isinstance(data, dict) and data.get("text") is None:
            data["text"] = data.get("content")
        return data


class ChatSummary(BaseModel):
    model_config = MODEL_CONFIG

    id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None
    last_message: str | None = None


class ChatDetailResponse(BaseResponse):
    model_config = MODEL_CONFIG

    chat_id: str
    title: str
    messages: list[ChatMessage] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
    last_message: str | None = None


class ChatListResponse(BaseResponse):
    model_config = MODEL_CONFIG

    chats: list[ChatSummary] = Field(default_factory=list)


class ChatResponse(BaseResponse):
    model_config = MODEL_CONFIG

    chat_id: str | None = None
    domain: DomainType
    data: ResponseData | None = None  # typed domain data dict
    response: str  # formatted string (backward compat)
    messages: list[ChatMessage] | None = None


class ErrorResponse(BaseResponse):
    model_config = MODEL_CONFIG

    success: bool = False


class TokenResponse(BaseModel):
    model_config = MODEL_CONFIG

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    username: str | None = None
    name: str | None = None
    email: str | None = None


class RegisterResponse(BaseModel):
    model_config = MODEL_CONFIG

    username: str
    name: str | None = None
    email: str | None = None


# PDF response models
class PDFMetadata(BaseModel):
    model_config = MODEL_CONFIG

    filename: str | None = None
    pages: int | None = None
    chunks: int | None = None

class PDFLoadResponse(BaseResponse, PDFMetadata):
    model_config = MODEL_CONFIG

    message: str


class PDFStatusResponse(PDFMetadata):
    model_config = MODEL_CONFIG
    loaded: bool


class PDFAnswerResponse(BaseResponse):
    model_config = MODEL_CONFIG

    response: str
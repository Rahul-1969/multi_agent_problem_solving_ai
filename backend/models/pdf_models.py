"""PDF-specific request and response models."""

from pydantic import BaseModel, Field

from backend.models.response_models import BaseResponse, MODEL_CONFIG


class PDFQuestionRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Question about the PDF")
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for PDF-specific state. Defaults to 'default'.",
    )


class PDFLoadRequest(BaseModel):
    path: str = Field(..., min_length=1, description="Server-side path to the PDF file")
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for PDF-specific state. Defaults to 'default'.",
    )


class PDFMetadata(BaseModel):
    model_config = MODEL_CONFIG

    session_id: str | None = None
    filename: str | None = None
    pages: int | None = None
    chunks: int | None = None


class PDFLoadResponse(BaseResponse, PDFMetadata):
    model_config = MODEL_CONFIG

    message: str


class PDFStatusResponse(PDFMetadata):
    model_config = MODEL_CONFIG

    loaded: bool


class PDFAnswerResponse(BaseResponse, PDFMetadata):
    model_config = MODEL_CONFIG

    response: str

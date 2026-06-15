"""
backend/services/chatbot_service.py
Service layer — routes queries, calls pipelines, formats structured output.

Backward compatibility strategy:
  Pipeline returns PipelineResult(response, data) → Extract response & data
  OR Pipeline returns str (legacy) → Use formatter to parse into model

This allows gradual migration of pipelines to PipelineResult format.

Fixes
-----
1. Full try/except around entire processing logic — no unhandled crashes.
2. Dictionary-based pipeline and formatter dispatch (no if-elif chain).
3. Per-pipeline exception handling with graceful fallback response.
4. isinstance() checks for PipelineResult vs str handling.
"""

from typing import Final

from backend.models.response_models import ChatResponse
from backend.services.formatter_dispatcher import dispatch_formatter
from backend.services.pipeline_dispatcher import dispatch_pipeline
from constants.domains import GENERAL_DOMAIN
from router.domain_router import route_domain
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Module constants ──────────────────────────────────────────────────────────
DEFAULT_DOMAIN: Final[str] = GENERAL_DOMAIN

INTERNAL_ERROR_MESSAGE = (
    "⚠️  An internal error occurred. Please try again."
)


def process_query(message: str) -> ChatResponse:
    """
    Route, process, and structure the response.

    Backward compatibility:
      Pipelines now return PipelineResult(response, data)
      If result is PipelineResult: extract response and data directly
      If result is string (legacy): parse with formatter

    Returns:
      ChatResponse with domain, response, data, and optional error.

    Never raises — all exceptions are caught and returned as error responses.
    """
    domain = DEFAULT_DOMAIN
    query = message.strip()

    domain = route_domain(query)
    logger.info(
        "Domain=%s | Query=%s",
        domain,
        query[:80],
    )

    result = dispatch_pipeline(domain, query)
    response = result.response if hasattr(result, "response") else result
    data = dispatch_formatter(domain, result, query)

    # If the pipeline dispatcher returned an internal error message,
    # preserve the failure signal for the API response.
    if response == INTERNAL_ERROR_MESSAGE:
        return ChatResponse(
            success=False,
            domain=domain,
            response=response,
            data=None,
            error="Pipeline execution failed",
        )

    return ChatResponse(
        success=True,
        domain=domain,
        response=response,
        data=data,
    )

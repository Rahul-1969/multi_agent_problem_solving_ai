"""
backend/services/formatter_dispatcher.py
Formatter dispatch responsibility.

This module converts pipeline output into structured data for the API.
It handles both new PipelineResult payloads and legacy string responses.
"""

from utils.logger import get_logger
from collections.abc import Callable
from typing import Any, Final, TypeAlias

from agents.extractor_agent import extract_student_info
from backend.models.response_models import ResponseData
from constants.domains import (
    COLLEGE_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
    MEDICAL_DOMAIN,
)
from pipelines.pipeline_result import PipelineResult
from utils.response_formatter import (
    format_coding,
    format_education,
    format_general,
    format_medical,
    format_college,
)

logger = get_logger(__name__)

FormatterFunction: TypeAlias = Callable[[str, str], dict[str, Any]]
FormatterMap: TypeAlias = dict[str, FormatterFunction]

_FORMATTERS: Final[FormatterMap] = {
    COLLEGE_DOMAIN: lambda response, query: format_college(response, extract_student_info(query)).model_dump(),
    MEDICAL_DOMAIN: lambda response, query: format_medical(response).model_dump(),
    CODING_DOMAIN: lambda response, query: format_coding(response).model_dump(),
    EDUCATION_DOMAIN: lambda response, query: format_education(response, query).model_dump(),
    GENERAL_DOMAIN: lambda response, query: format_general(response).model_dump(),
}


def _format(domain: str, response: str, query: str) -> dict[str, Any] | None:
    """
    Legacy formatter entry point.

    Used when the pipeline returned a plain string.
    """
    try:
        formatter = _FORMATTERS.get(domain, _FORMATTERS["general"])
        return formatter(response, query)
    except Exception:
        logger.exception("Formatter failed | domain=%s", domain)
        raise


def dispatch_formatter(
    domain: str,
    pipeline_output: str | PipelineResult,
    query: str,
) -> dict[str, Any] | None:
    """
    Dispatch structured formatting for pipeline output.

    If the pipeline already returned a PipelineResult with structured data,
    return the model dump directly. Otherwise, parse legacy string output.
    """
    logger.info("Formatter dispatched | domain=%s", domain)

    if isinstance(pipeline_output, PipelineResult):
        if pipeline_output.data is not None:
            logger.debug(
                "Using structured data from PipelineResult | type=%s",
                type(pipeline_output.data).__name__,
            )
            return pipeline_output.data.model_dump()
        return _format(domain, pipeline_output.response, query)

    return _format(domain, pipeline_output, query)

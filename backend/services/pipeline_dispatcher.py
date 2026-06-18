"""
backend/services/pipeline_dispatcher.py
Pipeline dispatch responsibility.

This module selects and executes the correct pipeline for a domain.
It isolates pipeline selection and exception handling from chatbot_service.
"""

from collections.abc import Callable
from typing import Final, TypeAlias

from constants.domains import (
    COLLEGE_DOMAIN,
    CODING_DOMAIN,
    EDUCATION_DOMAIN,
    GENERAL_DOMAIN,
    MEDICAL_DOMAIN,
    PDF_DOMAIN,
)
from pipelines.pipeline_result import PipelineResult
from pipelines.college_pipeline import college_pipeline
from pipelines.coding_pipeline import coding_pipeline
from pipelines.education_pipeline import education_pipeline
from pipelines.general_pipeline import general_pipeline
from pipelines.medical_pipeline import medical_pipeline
from pipelines.pdf_pipeline import pdf_pipeline
from tools.pdf_session_manager import DEFAULT_SESSION_ID, pdf_session_manager
from utils.logger import get_logger

logger = get_logger(__name__)

PipelineOutput: TypeAlias = str | PipelineResult
PipelineMap: TypeAlias = dict[str, Callable[[str], PipelineOutput]]

_DEFAULT_DOMAIN: Final[str] = GENERAL_DOMAIN


def _pdf_pipeline_wrapper(query: str) -> str:
    """Adapter so pdf_pipeline fits the standard dispatch signature."""
    if not pdf_session_manager.is_loaded(DEFAULT_SESSION_ID):
        return "No PDF loaded. Please upload a PDF first using /pdf/load."
    store = pdf_session_manager.get_store(DEFAULT_SESSION_ID)
    return pdf_pipeline(query, store.chunks, store.filename)


_PIPELINES: Final[PipelineMap] = {
    COLLEGE_DOMAIN: college_pipeline,
    MEDICAL_DOMAIN: medical_pipeline,
    CODING_DOMAIN: coding_pipeline,
    EDUCATION_DOMAIN: education_pipeline,
    GENERAL_DOMAIN: general_pipeline,
    PDF_DOMAIN: _pdf_pipeline_wrapper,
}


def dispatch_pipeline(domain: str, query: str) -> PipelineOutput:
    """
    Dispatch the pipeline for a given domain.

    This function is responsible for:
    - pipeline selection
    - pipeline execution
    - pipeline exception handling
    - fallback to general pipeline
    """
    logger.info("Pipeline dispatched | domain=%s", domain)
    pipeline = _PIPELINES.get(domain, general_pipeline)

    try:
        return pipeline(query)
    except Exception:
        logger.exception("Pipeline failed | domain=%s", domain)
        try:
            logger.info(
                "Falling back to general pipeline | original_domain=%s",
                domain,
            )
            return general_pipeline(query)
        except Exception:
            logger.exception(
                "General fallback pipeline also failed | query=%s",
                query[:80],
            )
            raise

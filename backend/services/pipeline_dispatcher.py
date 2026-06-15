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
)
from pipelines.pipeline_result import PipelineResult
from pipelines.college_pipeline import college_pipeline
from pipelines.coding_pipeline import coding_pipeline
from pipelines.education_pipeline import education_pipeline
from pipelines.general_pipeline import general_pipeline
from pipelines.medical_pipeline import medical_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

PipelineOutput: TypeAlias = str | PipelineResult
PipelineMap: TypeAlias = dict[str, Callable[[str], PipelineOutput]]

_DEFAULT_DOMAIN: Final[str] = GENERAL_DOMAIN

_PIPELINES: Final[PipelineMap] = {
    COLLEGE_DOMAIN: college_pipeline,
    MEDICAL_DOMAIN: medical_pipeline,
    CODING_DOMAIN: coding_pipeline,
    EDUCATION_DOMAIN: education_pipeline,
    GENERAL_DOMAIN: general_pipeline,
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

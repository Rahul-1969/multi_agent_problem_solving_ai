"""
pipelines/pipeline_result.py
Unified pipeline result container.

Transition architecture:
    Old: Pipeline → str → ResponseFormatter → Pydantic model
    New: Pipeline → PipelineResult → Pydantic model

This dataclass enables pipelines to return structured data alongside
the formatted response, allowing gradual migration of formatting logic
out of response_formatter.py.

Backward compatibility maintained via chatbot_service isinstance() checks.
"""

from dataclasses import dataclass
from typing import Final, TypeAlias

from backend.models.response_models import (
    EducationData,
    MedicalData,
    CodingData,
    CollegeCard,
    CollegeData,
    GeneralData,
    ResponseData,
)


# Type aliases for clarity and extensibility
PipelineData: TypeAlias = EducationData | MedicalData | CodingData | CollegeData | GeneralData | None


@dataclass(slots=True)
class PipelineResult:
    """
    Container for pipeline output combining both formatted string
    and structured data for gradual formatter deprecation.

    Fields:
        response: The formatted string (for backward compatibility and display)
        data: The parsed structured data model (domain-specific)

    Example:
        >>> result = PipelineResult(
        ...     response="📚 Definition...",
        ...     data=EducationData(topic="DBMS", definition="...")
        ... )
        >>> assert isinstance(result.data, EducationData)
    """

    response: str
    data: PipelineData = None

    def __post_init__(self) -> None:
        """Validate response is not empty."""
        if not self.response or not isinstance(self.response, str):
            raise ValueError("response must be a non-empty string")

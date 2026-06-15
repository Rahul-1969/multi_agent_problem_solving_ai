"""
schemas/education_schema.py
Canonical label definitions for education domain.

Canonical section names used in formatting:
  - definition: Topic definition
  - key_points: Important points/features
  - example: Worked example or use case
  - exam_tip: Exam-relevant tip

These labels are used by:
  - education_pipeline: To structure LLM output
  - response_formatter: To parse formatted strings
  - schema_parser: To extract sections
"""

from typing import Final, TypeAlias, Mapping


LabelMap: TypeAlias = Mapping[str, list[str]]


EDUCATION_LABELS: Final[LabelMap] = {
    "definition": ["📖  Definition"],
    "key_points": ["🔑  Key Points"],
    "example": ["💡  Example"],
    "exam_tip": ["🎯  Exam Tip"],
}


__all__ = ["EDUCATION_LABELS", "LabelMap"]

"""
schemas/medical_schema.py
Canonical label definitions for medical domain.

Canonical section names used in formatting:
  - conditions: Possible medical conditions/diagnoses
  - treatments: Safe OTC treatments and remedies
  - lifestyle: Lifestyle, diet, and precaution tips
  - emergency: Red flags requiring immediate medical attention

These labels are used by:
  - medical_pipeline: To structure LLM output
  - response_formatter: To parse formatted strings
  - schema_parser: To extract sections
"""

from typing import Final, TypeAlias, Mapping


LabelMap: TypeAlias = Mapping[str, list[str]]


MEDICAL_LABELS: Final[LabelMap] = {
    "conditions": ["📋  Possible Conditions"],
    "treatments": ["💊  Safe Treatments"],
    "lifestyle": ["🥗  Lifestyle & Precautions"],
    "emergency": ["🚨  Seek Immediate Medical Attention If"],
}


__all__ = ["MEDICAL_LABELS", "LabelMap"]

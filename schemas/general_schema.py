"""
schemas/general_schema.py
Schema definitions for general domain.

The general domain uses GeneralData which contains only the answer field,
so no specific labels are needed here. This file serves as a placeholder
for consistency and future extensibility.

GeneralData model:
    answer: str - The response text from general_pipeline

Used by:
  - general_pipeline: Returns GeneralData with answer
  - response_formatter: Parses into GeneralData
  - schema_parser: General domain doesn't use structured labels
"""

from typing import Final


# General domain doesn't require structured labels
# It uses a simple answer field in GeneralData
GENERAL_LABELS: Final[dict] = {}


__all__ = ["GENERAL_LABELS"]

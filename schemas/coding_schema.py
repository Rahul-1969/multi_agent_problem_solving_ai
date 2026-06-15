"""
schemas/coding_schema.py
Canonical label definitions for coding domain.

Canonical section names used in formatting:
  - explanation: Code explanation and walkthrough
  - complexity: Time and space complexity analysis
  - tip: Edge cases, optimizations, or important tips

These labels are used by:
  - coding_pipeline: To structure LLM output
  - response_formatter: To parse formatted strings
  - schema_parser: To extract sections
"""

from typing import Final, TypeAlias, Mapping


LabelMap: TypeAlias = Mapping[str, list[str]]


CODING_LABELS: Final[LabelMap] = {
    "explanation": ["EXPLANATION"],
    "complexity": ["COMPLEXITY"],
    "tip": ["TIP", "EDGE CASE", "OPTIMIZATION"],
}


__all__ = ["CODING_LABELS", "LabelMap"]

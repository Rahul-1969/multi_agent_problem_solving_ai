"""
utils/response_formatter.py
BACKWARD COMPATIBILITY LAYER — Will eventually disappear once pipelines
return structured models.

Centralised response formatter layer.

Sits between pipelines and the API routes:
  Pipeline (raw string)
    ↓
  ResponseFormatter  ← THIS FILE (DEPRECATED)
    ↓
  API Response (structured data + formatted string)

Each pipeline returns a plain formatted string.
This module parses that string into structured data fields
AND returns the original string for backward compatibility.

Architecture (Being Phased Out)
-------------------------------
The formatter uses the same label-parsing logic as the pipelines
but operates on the FINAL output rather than the raw LLM output.
This keeps pipelines decoupled from API concerns.

Future State
------------
Pipelines will return PipelineResult(response, data) directly,
eliminating the need for this formatter entirely.

Performance
-----------
All regex patterns are precompiled to avoid repeated compilation on each call.
"""

import re
from collections.abc import Mapping
from typing import Final, TypeAlias
from backend.models.response_models import (
    EducationData, MedicalData, CodingData,
    CollegeData, GeneralData
)
from utils.section_parser import parse_sections
from schemas.education_schema import EDUCATION_LABELS
from schemas.medical_schema import MEDICAL_LABELS
from schemas.coding_schema import CODING_LABELS

# ──────────────────────────────────────────────────────────────────────────────
# Type aliases and module constants
# ──────────────────────────────────────────────────────────────────────────────

Pattern: TypeAlias = re.Pattern[str]
LabelMap: TypeAlias = Mapping[str, list[str]]

_DEFAULT_LANGUAGE: Final[str] = "python"
_CLARIFICATION_MARKER: Final[str] = "Did you mean:"

# ──────────────────────────────────────────────────────────────────────────────
# Helper functions (before regex patterns for logical flow)
# ──────────────────────────────────────────────────────────────────────────────

def _clean_section(text: str) -> str:
    """Remove divider lines and trim whitespace."""
    return _DIVIDER_PATTERN.sub("", text or "").strip()


def _parse_sections(
    response: str,
    labels: LabelMap,
) -> dict[str, str]:
    """
    Strip response and parse sections using the shared parser.
    """
    return parse_sections(response.strip(), labels)


def _append_tip(
    explanation: str,
    tip: str,
) -> str:
    """
    Append tip text to explanation while preserving formatting.
    """
    tip = tip.strip()
    if not tip:
        return explanation
    if explanation:
        return f"{explanation}\n{tip}"
    return tip


def _extract_college_list(
    response_str: str,
    pattern: Pattern,
    bullet_pattern: Pattern,
) -> list[str]:
    """
    Extract bullet-point items from a pattern match.
    Used by format_college to avoid function recreation per call.
    """
    m = pattern.search(response_str)
    if not m:
        return []
    section_text = m.group(1)
    names: list[str] = bullet_pattern.findall(section_text)
    return [n.strip() for n in names if n.strip()]

# ──────────────────────────────────────────────────────────────────────────────
# Precompiled regex patterns (one-time compilation)
# ──────────────────────────────────────────────────────────────────────────────

_DIVIDER_PATTERN: Pattern = re.compile(r'─{10,}')

# Import canonical label maps from schema files
# (Single source of truth — no local definitions)
# EDUCATION_LABELS imported from schemas.education_schema
# MEDICAL_LABELS imported from schemas.medical_schema
# CODING_LABELS imported from schemas.coding_schema

# Coding patterns
_SAFE_PATTERN: Pattern = re.compile(r'🟢.*?SAFE.*?\n(.*?)(?=🟡|🔴|─{10}|\Z)', re.DOTALL)
_MODERATE_PATTERN: Pattern = re.compile(r'🟡.*?MODERATE.*?\n(.*?)(?=🔴|─{10}|\Z)', re.DOTALL)
_DREAM_PATTERN: Pattern = re.compile(r'🔴.*?DREAM.*?\n(.*?)(?=─{10}|\Z)', re.DOTALL)
_BULLET_PATTERN: Pattern = re.compile(r'•\s+(.+?)(?:\n|$)')

_COLLEGE_PATTERNS: Final[dict[str, Pattern]] = {
    "safe": _SAFE_PATTERN,
    "moderate": _MODERATE_PATTERN,
    "dream": _DREAM_PATTERN,
}


def _empty_coding_data() -> CodingData:
    """Return default empty CodingData response."""
    return CodingData(
        language=_DEFAULT_LANGUAGE,
        code="",
        explanation="",
        complexity=None,
    )


def _build_clarification_response(
    response: str,
) -> CodingData:
    """
    Build a clarification response with suggestions.
    """
    suggestions = _SUGGESTION_PATTERN.findall(response)
    return CodingData(
        language=None,
        code=None,
        explanation=None,
        complexity=None,
        clarification=suggestions,
    )


def format_education(response_str: str, query: str) -> EducationData:
    """
    Parse education pipeline output into structured fields.
    Optimized for O(n) single-pass parsing.

    BACKWARD COMPATIBILITY: Will be deprecated once education_pipeline
    returns PipelineResult directly.
    """
    sections = _parse_sections(response_str, EDUCATION_LABELS)

    return EducationData(
        topic=query,
        definition=_clean_section(sections.get("definition", "")),
        key_points=_clean_section(sections.get("key_points", "")),
        example=_clean_section(sections.get("example", "")),
        exam_tip=_clean_section(sections.get("exam_tip", "")),
    )


def format_medical(response_str: str) -> MedicalData:
    """
    Parse medical pipeline output into structured fields.

    BACKWARD COMPATIBILITY: Will be deprecated once medical_pipeline
    returns PipelineResult directly.
    """
    sections = _parse_sections(response_str, MEDICAL_LABELS)

    return MedicalData(
        conditions=_clean_section(sections.get("conditions", "")),
        treatments=_clean_section(sections.get("treatments", "")),
        lifestyle=_clean_section(sections.get("lifestyle", "")),
        emergency=_clean_section(sections.get("emergency", "")),
    )


def format_coding(response_str: str) -> CodingData:
    """
    Parse coding pipeline output into structured fields.

    BACKWARD COMPATIBILITY: Will be deprecated once coding_pipeline
    returns PipelineResult directly.
    """
    response = response_str.strip()

    if _CLARIFICATION_MARKER in response:
        return _build_clarification_response(response)

    # Extract code block and language in one pass
    code_m = _CODE_PATTERN.search(response)
    if not code_m:
        return _empty_coding_data()

    language = code_m.group(1) or _DEFAULT_LANGUAGE
    code = code_m.group(2).strip()
    after_code = response[code_m.end():].strip()

    # Parse sections from the post-code content
    sections = parse_sections(after_code, CODING_LABELS)

    # Build explanation from explanation section
    explanation_text = sections.get("explanation", "").strip()
    explanation_text = _append_tip(
        explanation_text,
        sections.get("tip", ""),
    )

    # Get complexity section
    complexity = sections.get("complexity", "").strip() or None

    return CodingData(
        language=language,
        code=code,
        explanation=explanation_text,
        complexity=complexity,
    )


def format_college(
    response_str: str,
    extracted_info: dict | None = None
) -> CollegeData:
    """Parse college pipeline output into structured fields."""
    response = response_str.strip()

    # Extract all sections using dictionary comprehension
    sections: dict[str, list[str]] = {
        key: _extract_college_list(response, pattern, _BULLET_PATTERN)
        for key, pattern in _COLLEGE_PATTERNS.items()
    }

    info = extracted_info or {}
    return CollegeData(
        rank=info.get("rank"),
        category=info.get("category"),
        gender=info.get("gender"),
        branch=info.get("preferred_branch"),
        location=info.get("location"),
        safe=sections["safe"],
        moderate=sections["moderate"],
        dream=sections["dream"],
    )


def format_general(response_str: str) -> GeneralData:
    return GeneralData(answer=response_str.strip())
"""
utils/schema_parser.py
High-level schema-based section parsing.

This module provides a convenient wrapper around section_parser that
simplifies parsing using pre-defined schema label maps, ensuring all
section extraction flows through a single, testable utility.

Architecture:
    parse_by_schema(text, labels) → section_parser.parse_sections(text, labels)

This indirection allows future enhancements (caching, validation, logging)
without modifying section_parser.
"""

from typing import Mapping, Sequence

from utils.section_parser import parse_sections as _section_parse


# Type alias matching section_parser conventions
LabelMap = Mapping[str, Sequence[str]]


def parse_by_schema(
    text: str,
    labels: LabelMap,
) -> dict[str, str]:
    """
    Parse labeled sections from text using a pre-defined schema.

    This is the canonical entry point for all schema-based section parsing.
    Internally delegates to section_parser.parse_sections() to avoid
    duplicating label extraction logic.

    Args:
        text: Raw LLM output or pipeline response text
        labels: Schema label map (canonical name → list of aliases)

    Returns:
        dict mapping canonical section names to extracted content.
        Missing sections are empty strings.

    Example:
        >>> from schemas.education_schema import EDUCATION_LABELS
        >>> text = "DEFINITION:\\nA computer network..."
        >>> sections = parse_by_schema(text, EDUCATION_LABELS)
        >>> print(sections["definition"])
        'A computer network...'
    """
    return _section_parse(text, labels)


__all__ = ["parse_by_schema", "LabelMap"]

"""Utility for parsing labeled sections from LLM text output.

This module provides a reusable parser that can identify named sections
based on a canonical label map and extract the content that follows each
section header.
"""

from functools import cache
import re
from typing import Pattern, Mapping, Sequence

# Type alias for the incoming label map (preserves insertion order).
SectionMap = Mapping[str, Sequence[str]]

# Regex flags used for label matching (precompiled constant).
# Exported here only for internal reuse by the module's cached compiler.
_LABEL_FLAGS = re.IGNORECASE | re.MULTILINE


def _normalize_label(label: str) -> str:
    """Return a normalized label key for canonical lookup."""
    return label.strip().lower()


@cache
def _compile_section_pattern(
    label_map_items: tuple[tuple[str, tuple[str, ...]], ...]
) -> tuple[Pattern[str], dict[str, str]]:
    """Build and cache the compiled regex pattern and alias lookup map."""
    alias_to_canonical: dict[str, str] = {}
    alias_patterns: list[str] = []

    for canonical_name, aliases in label_map_items:
        for alias in aliases:
            normalized_alias = alias.strip()
            if not normalized_alias:
                continue
            alias_patterns.append(re.escape(normalized_alias))
            alias_to_canonical[_normalize_label(normalized_alias)] = canonical_name

    # Sort aliases longest-first to avoid partial matches in alternation.
    alias_patterns.sort(key=len, reverse=True)
    alternation = '|'.join(alias_patterns)

    # Match section labels at the start of lines, with optional colon.
    # Support both "LABEL:\n<text>" and "LABEL: <text>" formats by
    # consuming label and optional trailing colon/spaces but not the
    # following text.
    pattern = re.compile(
        rf'^[ \t]*(?P<label>{alternation})[ \t]*:?[ \t]*(?:\r?\n|$)',
        _LABEL_FLAGS,
    )
    return pattern, alias_to_canonical


def parse_sections(
    text: str,
    label_map: SectionMap,
    capture_leading_text: bool = False,
    merge_duplicates: bool = True,
) -> dict[str, str]:
    """Parse labeled sections from LLM output.

    Args:
        text: Raw text output from an LLM.
        label_map: Mapping of canonical section names to label aliases.
        capture_leading_text: When True, any text before the first found
            label is assigned to the first canonical section (if labels
            are found). Default False.
        merge_duplicates: When True and a canonical section appears
            multiple times, subsequent occurrences are appended to the
            existing content separated by two newlines. Default True.

    Returns:
        A dict mapping each canonical section name to the extracted content.
        Missing sections are returned as empty strings.
    """
    normalized_text = text or ""
    result: dict[str, str] = {canonical: "" for canonical in label_map}

    if not normalized_text.strip() or not label_map:
        return result

    # Preserve the insertion order of the provided mapping
    label_map_items = tuple(
        (canonical, tuple(aliases))
        for canonical, aliases in label_map.items()
    )
    pattern, alias_to_canonical = _compile_section_pattern(label_map_items)

    # Use a tuple for single-pass iteration results (immutable, indexable)
    matches = tuple(pattern.finditer(normalized_text))
    if not matches:
        return result

    # Optionally capture any leading text prior to the first label.
    if capture_leading_text:
        leading = normalized_text[: matches[0].start()].strip()
        if leading:
            # Use the first key from the original mapping to preserve
            # the caller's intended canonical ordering.
            first_canonical = next(iter(label_map))
            if merge_duplicates and result[first_canonical]:
                result[first_canonical] = f"{result[first_canonical]}\n\n{leading}"
            else:
                result[first_canonical] = leading

    for index, match in enumerate(matches):
        label_text = match.group('label')
        canonical_name = alias_to_canonical[_normalize_label(label_text)]
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized_text)
        content = normalized_text[start:end].strip()
        if merge_duplicates and result[canonical_name]:
            if content:
                result[canonical_name] = f"{result[canonical_name]}\n\n{content}"
        elif content:
            result[canonical_name] = content

    return result

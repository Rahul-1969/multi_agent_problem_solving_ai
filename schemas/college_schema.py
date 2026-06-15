"""Canonical label definitions for the college domain."""

from typing import Final, TypeAlias, Mapping

LabelMap: TypeAlias = Mapping[str, list[str]]

COLLEGE_LABELS: Final[LabelMap] = {
    "rank": ["RANK"],
    "category": ["CATEGORY"],
    "gender": ["GENDER"],
    "branch": ["BRANCH"],
    "location": ["LOCATION"],
    "safe": ["SAFE"],
    "moderate": ["MODERATE"],
    "dream": ["DREAM"],
}


__all__ = ["COLLEGE_LABELS", "LabelMap"]

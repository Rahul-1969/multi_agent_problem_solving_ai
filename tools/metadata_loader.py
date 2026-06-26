"""
tools/metadata_loader.py
Loads and caches the college_metadata.json lookup.

Usage in pipelines:
    from tools.metadata_loader import get_college_meta, load_college_metadata

    meta = get_college_meta("CVRH")     # returns enriched dict or DEFAULT_META
    all_meta = load_college_metadata()  # returns full dict (for startup preload)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

from utils.logger import get_logger

logger = get_logger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────

_METADATA_PATH: Final[Path] = (
    Path(__file__).parent.parent / "data" / "college_metadata.json"
)

# ─── Default metadata used for colleges not in the JSON ───────────────────────

DEFAULT_META: Final[dict[str, Any]] = {
    "display_name": None,
    "autonomous": False,
    "affiliated_to": "JNTUH",
    "college_type": "Private",
    "naac_grade": "N/A",
    "nba_accredited": False,
    "nirf_rank": None,
    "established": None,
    "location_display": "Telangana",
    "available_branches": [],
    "avg_package_lpa": None,
    "highest_package_lpa": None,
    "median_package_lpa": None,
    "placement_percentage": None,
    "top_recruiters": [],
    "hostel_available": False,
    "scholarships_available": False,
    "official_website": None,
    "google_maps_url": None,
    "college_image_url": None,
    "quality_score": 0.0,
    "popularity_score": 0.0,
}

# ─── Module-level cache (loaded once per process) ─────────────────────────────

_metadata: dict[str, dict[str, Any]] | None = None


def load_college_metadata() -> dict[str, dict[str, Any]]:
    """
    Return the full college metadata dict (cached after first call).

    Thread-safe for read operations — the dict is loaded once and
    treated as immutable after startup.
    """
    global _metadata

    if _metadata is not None:
        logger.debug("Using cached college metadata.")
        return _metadata

    if not _METADATA_PATH.exists():
        logger.warning(
            "College metadata file not found at %s. Using empty dict.", _METADATA_PATH
        )
        _metadata = {}
        return _metadata

    logger.info("Loading college metadata from %s", _METADATA_PATH)
    try:
        with open(_METADATA_PATH, encoding="utf-8") as fh:
            raw: dict[str, Any] = json.load(fh)

        # Drop the _comment key if present (documentation artifact)
        raw.pop("_comment", None)

        _metadata = raw
        logger.info("Loaded metadata for %d colleges.", len(_metadata))
    except Exception:
        logger.exception("Failed to load college metadata. Falling back to empty dict.")
        _metadata = {}

    return _metadata


def get_college_meta(college_code: str) -> dict[str, Any]:
    """
    Return enriched metadata for a given college code.

    Falls back to DEFAULT_META for any code not present in the JSON,
    so callers never need to handle a missing-key case.
    """
    return load_college_metadata().get(college_code, DEFAULT_META)

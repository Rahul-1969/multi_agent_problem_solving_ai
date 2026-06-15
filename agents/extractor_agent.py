"""
agents/extractor_agent.py
Rule-based NLP extractor for college predictor inputs.

Extracts: rank, category, gender, location, preferred_branch
from a free-form natural language query.
"""

import re
from utils.logger import get_logger
logger = get_logger(__name__)

# ─── Mappings ─────────────────────────────────────────────────────────────────

CATEGORY_MAP: dict[str, str] = {
    # OC / General
    "oc":      "OC",
    "general": "OC",
    "open":    "OC",
    # BC variants
    "bc_a": "BC_A", "bca": "BC_A", "bc a": "BC_A",
    "bc_b": "BC_B", "bcb": "BC_B", "bc b": "BC_B",
    "bc_c": "BC_C", "bcc": "BC_C", "bc c": "BC_C",
    "bc_d": "BC_D", "bcd": "BC_D", "bc d": "BC_D",
    "bc_e": "BC_E", "bce": "BC_E", "bc e": "BC_E",
    # SC / ST
    "sc": "SC",
    "st": "ST",
    # EWS
    "ews": "EWS",
    "economically weaker": "EWS",
}

GENDER_MAP: dict[str, str] = {
    "female": "GIRLS", "girl": "GIRLS", "girls": "GIRLS", "woman": "GIRLS", "women": "GIRLS",
    "male":   "BOYS",  "boy":  "BOYS",  "boys":  "BOYS",  "man":   "BOYS",  "men":   "BOYS",
}

CITY_MAP: dict[str, str] = {
    "hyderabad":    "hyderabad",
    "hyd":          "hyderabad",
    "secunderabad": "hyderabad",
    "rangareddy":   "rangareddy",
    "rr":           "rangareddy",
    "sangareddy":   "sangareddy",
    "medak":        "medak",
    "warangal":     "warangal",
    "wgl":          "warangal",
    "hanamkonda":   "warangal",
    "karimnagar":   "karimnagar",
    "khammam":      "khammam",
    "nalgonda":     "nalgonda",
    "nizamabad":    "nizamabad",
    "suryapet":     "suryapet",
    "siddipet":     "siddipet",
    "yadadri":      "yadadri",
    "mahabubnagar": "mahabubnagar",
}

BRANCH_MAP: dict[str, str] = {
    "cse":                 "CSE",
    "computer science":    "CSE",
    "computers":           "CSE",
    "cs":                  "CSE",
    "ece":                 "ECE",
    "electronics":         "ECE",
    "eee":                 "EEE",
    "electrical":          "EEE",
    "mechanical":          "MEC",
    "mech":                "MEC",
    "civil":               "CIV",
    "information technology": "INF",
    "it":                  "INF",
    "inf":                 "INF",
    "ai":                  "AI",
    "artificial intelligence": "AI",
    "aiml":                "AI",
    "machine learning":    "AI",
    "chemical":            "CHE",
    "metallurgy":          "MET",
    "mining":              "MIN",
}


# ─── Extractor ────────────────────────────────────────────────────────────────

def extract_student_info(query: str) -> dict | None:
    """
    Parse a free-form query and return a dict with keys:
        rank, category, gender, location, preferred_branch
    Returns None if the mandatory fields (rank, category, gender) are missing.
    """

    q = query.lower().replace("-", "_")

    # ── Rank ─────────────────────────────────────────────────────────────────
    rank: int | None = None
    # Match "rank 12345" or standalone 3-6 digit numbers
    rank_patterns = [
        r"rank\s*[:\-]?\s*(\d{3,6})",
        r"(?<!\d)(\d{3,6})(?!\d)",
    ]
    for pat in rank_patterns:
        m = re.search(pat, q)
        if m:
            rank = int(m.group(1))
            break

    # ── Category ─────────────────────────────────────────────────────────────
    category: str | None = None
    # Sort by length descending so longer keys match first (e.g. "bc_a" before "bc")
    for key in sorted(CATEGORY_MAP, key=len, reverse=True):
        if key in q:
            category = CATEGORY_MAP[key]
            break

    # ── Gender ───────────────────────────────────────────────────────────────
    gender: str | None = None
    for key in sorted(GENDER_MAP, key=len, reverse=True):
        if re.search(r"\b" + re.escape(key) + r"\b", q):
            gender = GENDER_MAP[key]
            break

    # ── Location ─────────────────────────────────────────────────────────────
    location: str | None = None
    for key in sorted(CITY_MAP, key=len, reverse=True):
        if key in q:
            location = CITY_MAP[key]
            break

    # ── Branch ───────────────────────────────────────────────────────────────
    branch = "NONE"
    for key in sorted(BRANCH_MAP, key=len, reverse=True):
        if key in q:
            branch = BRANCH_MAP[key]
            break

    # ── Validate mandatory fields ─────────────────────────────────────────────
    if rank is None or category is None or gender is None:
        logger.debug(
            "Extraction incomplete → rank=%s category=%s gender=%s",
            rank, category, gender
        )
        return None

    return {
        "rank":            rank,
        "category":        category,
        "gender":          gender,
        "location":        location,
        "preferred_branch": branch,
    }

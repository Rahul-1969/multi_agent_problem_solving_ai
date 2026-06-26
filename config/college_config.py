"""College predictor configuration."""

from typing import Final

TOP_COLLEGES: Final[set[str]] = {
    "JNTUH", "OUCE", "CBIT", "VNRV", "VJEC", "MVSR", "GCTC", "SNIS",
    "CMRK", "KMIT", "IARE", "BVRI", "MGIT", "MREC", "MLID", "MRCET",
    "CMRM", "VMEG", "ANRK", "SRTI", "TKRC", "NRCM", "KPRT", "MRECW",
    "GRRR", "JBIT", "ACEG", "AARM", "VBIT", "KGRH", "NGIT", "MATR",
    "CMRG", "DRKI", "AVNI", "GATE", "BRIL", "ELEN", "INDU", "SMSK",
    "SITS", "VJIT", "SRHP", "KUCE", "KITS", "VCEW", "STMW", "HITM",
    "CITS", "AURG",
}

TOP_RESULTS_TARGET: Final[int] = int(
    __import__("os").getenv("TOP_RESULTS_TARGET", "20")
)
SAFE_THRESHOLD: Final[int] = int(
    __import__("os").getenv("SAFE_THRESHOLD", "10000")
)
MODERATE_THRESHOLD: Final[int] = int(
    __import__("os").getenv("MODERATE_THRESHOLD", "3000")
)

LOCATION_MAP: Final[dict[str, list[str]]] = {
    "hyderabad":    ["HYD", "RR"],
    "hyd":          ["HYD", "RR"],
    "secunderabad": ["HYD", "RR"],
    "warangal":     ["WGL"],
    "wgl":          ["WGL"],
    "karimnagar":   ["KMR"],
    "khammam":      ["KHM"],
    "medak":        ["MDL", "MED"],
    "nalgonda":     ["NLG"],
    "nizamabad":    ["NZB"],
    "mahabubnagar": ["MBN"],
    "rangareddy":   ["RR"],
    "rr":           ["RR"],
    "sangareddy":   ["SRD"],
    "siddipet":     ["SRP"],
    "yadadri":      ["YBN"],
    "suryapet":     ["SRP"],
}

import json
from pathlib import Path

# Load branch mappings dynamically
try:
    _branch_mapping_file = Path(__file__).parent / "branch_mapping.json"
    with open(_branch_mapping_file, "r", encoding="utf-8") as _f:
        BRANCH_MAP: Final[dict[str, list[str]]] = json.load(_f)
except Exception:
    BRANCH_MAP: Final[dict[str, list[str]]] = {}

__all__ = [
    "TOP_COLLEGES",
    "TOP_RESULTS_TARGET",
    "SAFE_THRESHOLD",
    "MODERATE_THRESHOLD",
    "LOCATION_MAP",
    "BRANCH_MAP",
]

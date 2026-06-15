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

BRANCH_MAP: Final[dict[str, list[str]]] = {
    "CSE": [
        "CSE",
        "CS",
        "CSM",
        "CSD",
        "CSO",
        "CSS",
        "CSBS",
        "CSE-AIML",
        "CSE-DS",
        "CSE-IOT",
        "CSE-SEC",
        "CSE-IS",
        "CSE-ML",
        "CSE-AI",
    ],
    "INF": ["INF", "IT"],
    "ECE": ["ECE", "ECA", "ECM"],
    "EEE": ["EEE"],
    "MEC": ["MEC", "MECH", "MEP"],
    "CIV": ["CIV"],
    "AI": [
        "AI",
        "AIML",
        "AID",
        "AIDS",
        "AI-DS",
        "AI-SEC",
        "AI-IS",
        "AI-ML",
        "AIML-DS",
        "CS-AI",
        "CS-AIML",
    ],
    "CHE": ["CHE", "CHEM"],
    "MET": ["MET"],
    "MIN": ["MIN"],
    "NONE": [],
}

__all__ = [
    "TOP_COLLEGES",
    "TOP_RESULTS_TARGET",
    "SAFE_THRESHOLD",
    "MODERATE_THRESHOLD",
    "LOCATION_MAP",
    "BRANCH_MAP",
]

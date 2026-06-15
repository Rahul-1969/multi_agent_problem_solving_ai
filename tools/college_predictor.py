"""
tools/college_predictor.py
Core college prediction engine.

Returns three DataFrames: (safe, moderate, dream).

Key fixes vs original
---------------------
1.  The original returned (top50, others) – but college_pipeline expected
    (safe, moderate, dream).  Signature is now correct.
2.  merge_colleges groupby preserved branch_code; now rebuilt cleanly.
3.  Location fallback added: if district filter yields 0 rows, retry
    without location so the user still gets results.
4.  DataFrame loaded lazily via data_loader (module-level cache → fast).
"""

import logging
import pandas as pd
from tools.data_loader import load_data
from config import (
    TOP_COLLEGES,
    TOP_RESULTS_TARGET,
    SAFE_THRESHOLD,
    MODERATE_THRESHOLD,
    LOCATION_MAP,
    BRANCH_MAP,
)
from utils.logger import get_logger

logger = get_logger(__name__)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _clean_name(row: pd.Series) -> str:
    name = " ".join(row["college_name"].replace("\n", " ").split()).title()
    return f"{name} ({row['college_code']})"


def _classify_chance(score: int) -> str:
    if score > SAFE_THRESHOLD:
        return "SAFE"
    elif score > MODERATE_THRESHOLD:
        return "MODERATE"
    else:
        return "DREAM"


def _merge_branches(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse multiple rows for the same college into one row,
    concatenating all branch codes (e.g. CSE/CSM/CSD).
    The best (lowest) score and the best (lowest) chance_rank are kept.
    """
    chance_order = {"SAFE": 0, "MODERATE": 1, "DREAM": 2}
    df = df.copy()
    df["_chance_rank"] = df["chance"].map(chance_order)

    grouped = (
        df.groupby("college_display", sort=False)
        .agg(
            branch_code  = ("branch_code",  lambda x: "/".join(sorted(set(x)))),
            priority     = ("priority",     "min"),
            score        = ("score",        "min"),
            _chance_rank = ("_chance_rank", "min"),
        )
        .reset_index()
    )

    rev = {v: k for k, v in chance_order.items()}
    grouped["chance"] = grouped["_chance_rank"].map(rev)
    grouped.drop(columns=["_chance_rank"], inplace=True)
    return grouped


# ─── Main predictor ───────────────────────────────────────────────────────────

def predict_colleges(
    rank: int,
    category: str,
    gender: str,
    location: str | None = None,
    branch_pref: str = "NONE",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Returns (safe_df, moderate_df, dream_df).
    Each DataFrame has columns: college_display, branch_code, chance, score.
    """

    df = load_data()

    logger.debug("predict_colleges → rank=%s cat=%s gender=%s branch=%s loc=%s",
                 rank, category, gender, branch_pref, location)

    # ── 1. Category / gender / rank filter ───────────────────────────────────
    result = df[
        (df["category"] == category) &
        (df["gender"]   == gender)   &
        (df["cutoff_rank"] >= rank)
    ].copy()

    # ── 2. Branch filter ──────────────────────────────────────────────────────
    if branch_pref and branch_pref.upper() != "NONE":
        branches = BRANCH_MAP.get(branch_pref.upper(), [branch_pref.upper()])
        result = result[result["branch_code"].isin(branches)]

    # ── 3. Location filter (with fallback) ────────────────────────────────────
    if location:
        districts = LOCATION_MAP.get(location.lower(), [])
        if districts:
            loc_result = result[result["district"].isin(districts)]
            if not loc_result.empty:
                result = loc_result
            else:
                logger.info("Location filter yielded 0 rows; ignoring location.")

    if result.empty:
        empty = pd.DataFrame(columns=["college_display", "branch_code", "chance", "score"])
        return empty, empty, empty

    # ── 4. Scoring ───────────────────────────────────────────────────────────
    result["score"]    = result["cutoff_rank"] - rank
    result["chance"]   = result["score"].apply(_classify_chance)
    result["priority"] = result["college_code"].apply(
        lambda c: 0 if c in TOP_COLLEGES else 1
    )

    # ── 5. Sort ───────────────────────────────────────────────────────────────
    result.sort_values(by=["priority", "score", "college_code"], inplace=True)

    # ── 6. Display name & branch merge ───────────────────────────────────────
    result["college_display"] = result.apply(_clean_name, axis=1)
    merged = _merge_branches(result)

    # ── 7. Top-50 priority selection ─────────────────────────────────────────
    top50  = merged[merged["priority"] == 0]
    others = merged[merged["priority"] == 1]

    if len(top50) >= TOP_RESULTS_TARGET:
        final = top50.head(TOP_RESULTS_TARGET)
    else:
        need  = TOP_RESULTS_TARGET - len(top50)
        final = pd.concat([top50, others.head(need)], ignore_index=True)

    # ── 8. Split by chance ────────────────────────────────────────────────────
    safe     = final[final["chance"] == "SAFE"].reset_index(drop=True)
    moderate = final[final["chance"] == "MODERATE"].reset_index(drop=True)
    dream    = final[final["chance"] == "DREAM"].reset_index(drop=True)

    logger.info("Results → SAFE:%d  MODERATE:%d  DREAM:%d",
                len(safe), len(moderate), len(dream))

    return safe, moderate, dream

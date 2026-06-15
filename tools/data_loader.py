"""
tools/data_loader.py
Loads and caches the EAMCET dataset.

Strategy
--------
• Uses the CSV file (≈7× faster than JSON for pandas).
• Module-level singleton – loaded once per process, never reloaded.
• Column names are normalised on load so downstream code never has to
  worry about trailing spaces or mixed casing.
• Thread-safe for read operations because the DataFrame
  is loaded once and treated as immutable.
"""

from pathlib import Path

import pandas as pd

from config import EAMCET_CSV

from utils.logger import get_logger

logger = get_logger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────────────
_STRING_COLUMNS = (
    "college_code",
    "college_name",
    "place",
    "district",
    "branch_code",
    "branch",
    "category",
    "gender",
)
_CUTOFF_COLUMN = "cutoff_rank"

# ─── Module-level cache ───────────────────────────────────────────────────────
_df: pd.DataFrame | None = None


def load_data() -> pd.DataFrame:
    """
    Return the EAMCET DataFrame (cached after first call).
    """
    global _df
    if _df is not None:
        logger.debug("Using cached EAMCET dataset.")
        return _df

    csv_path = Path(EAMCET_CSV)
    if not csv_path.exists():
        raise FileNotFoundError(f"EAMCET data not found at: {EAMCET_CSV}")

    logger.info("Loading EAMCET dataset from %s", csv_path)
    try:
        df = pd.read_csv(EAMCET_CSV, dtype=str, low_memory=False)
    except Exception:
        logger.exception("Failed to load EAMCET dataset")
        raise

    # Normalise column names
    df.columns = df.columns.str.strip().str.lower()

    # Type-cast numeric column
    df[_CUTOFF_COLUMN] = pd.to_numeric(df[_CUTOFF_COLUMN], errors="coerce")
    df = df.dropna(subset=[_CUTOFF_COLUMN]).copy()
    df[_CUTOFF_COLUMN] = df[_CUTOFF_COLUMN].astype(int)

    # Strip whitespace from string columns
    for col in _STRING_COLUMNS:
        if col in df.columns:
            df[col] = df[col].str.strip()

    logger.info("Loaded %d records.", len(df))
    _df = df
    return _df

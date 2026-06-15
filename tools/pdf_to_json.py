"""
tools/pdf_to_json.py
Convert EAMCET PDF to JSON format.

Performance optimizations:
• Parse pages directly without building intermediate string (low memory).
• Constants outside loops to avoid repeated allocations.
• List + join for string building (O(n) vs O(n²)).
"""

import json
from utils.logger import get_logger
from collections.abc import Iterator
from pathlib import Path

import pdfplumber

logger = get_logger(__name__)

# ==============================
# 📌 PATH SETUP (IMPORTANT)
# ==============================
BASE_DIR = Path(__file__).parent.parent
PDF_PATH = BASE_DIR / "data" / "Eamcet.pdf"
OUTPUT_PATH = BASE_DIR / "data" / "eamcet_data.json"

# ==============================
# 📌 CONSTANTS
# ==============================
BRANCH_KEYWORDS = {
    "CSE",
    "ECE",
    "EEE",
    "MEC",
    "CIV",
    "CSM",
    "INF",
}

CATEGORY_MAP = (
    "OC_BOYS",
    "OC_GIRLS",
    "BC_A_BOYS",
    "BC_A_GIRLS",
    "BC_B_BOYS",
    "BC_B_GIRLS",
    "BC_C_BOYS",
    "BC_C_GIRLS",
    "BC_D_BOYS",
    "BC_D_GIRLS",
    "BC_E_BOYS",
    "BC_E_GIRLS",
    "SC_BOYS",
    "SC_GIRLS",
    "ST_BOYS",
    "ST_GIRLS",
)


# ==============================
# 📌 STEP 1 & 2: EXTRACT & PARSE (optimized)
# ==============================
def extract_and_parse(pdf_path: str | Path) -> list[dict]:
    """
    Extract text from PDF and parse records directly.
    Avoids building intermediate giant string (low memory).
    """
    records = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()

                if not page_text:
                    continue

                logger.debug("Processed page %d", page_num)

                # Parse lines directly from this page
                records.extend(_parse_lines(page_text))
    except Exception:
        logger.exception("Failed to extract PDF")
        raise

    return records


def _parse_lines(text: str) -> Iterator[dict]:
    """
    Parse records from text lines (generator).
    """
    for line in text.splitlines():
        parts = line.split()

        if not parts:
            continue

        # Detect lines with many numbers (cutoff rows)
        numbers = [n for n in parts if n.isdigit()]

        if len(numbers) < 10:
            continue

        # Extract branch
        branch = None
        branch_index = -1

        for i, word in enumerate(parts):
            if word in BRANCH_KEYWORDS:
                branch = word
                branch_index = i
                break

        if branch is None:
            continue

        college = " ".join(parts[:branch_index])
        place = parts[branch_index - 1] if branch_index > 0 else ""

        # Extract category values
        for category, cutoff in zip(CATEGORY_MAP, map(int, numbers)):
            yield {
                "college": college,
                "place": place,
                "branch": branch,
                "category": category,
                "cutoff": cutoff,
            }


# ==============================
# 📌 STEP 3: SAVE JSON
# ==============================
def save_json(data: list[dict], output_path: str | Path) -> None:
    """
    Save records to JSON file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("JSON saved at: %s", output_path)
    except Exception:
        logger.exception("Failed to save JSON")
        raise


# ==============================
# 🚀 MAIN
# ==============================
if __name__ == "__main__":
    logger.info("Starting PDF → JSON conversion...")

    try:
        data = extract_and_parse(PDF_PATH)
        logger.info("Total records extracted: %d", len(data))
        save_json(data, OUTPUT_PATH)
        logger.info("Conversion complete!")
    except Exception:
        logger.error("Conversion failed", exc_info=True)
        raise
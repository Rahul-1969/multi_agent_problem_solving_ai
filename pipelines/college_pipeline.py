"""
pipelines/college_pipeline.py
Handles the full college prediction flow:
  Extract → Predict → Format output

Returns PipelineResult instead of plain strings to enable
structured data flow through the formatter layer.
"""

from agents.extractor_agent  import extract_student_info
from tools.college_predictor import predict_colleges
from pipelines.pipeline_result import PipelineResult
from backend.models.response_models import CollegeData


_DIVIDER = "─" * 55


def college_pipeline(query: str) -> PipelineResult:
    """
    Entry point for college prediction queries.
    Returns a PipelineResult with structured college data and formatted response.
    """

    # ── Step 1: Extract structured info from query ────────────────────────────
    user_data = extract_student_info(query)

    if not user_data:
        error_response = (
            "❌ Could not extract all required details.\n\n"
            "Please include:\n"
            "  • Rank          (e.g. 'my rank is 5000')\n"
            "  • Category      (e.g. OC / BC_A / BC_B / SC / ST / EWS)\n"
            "  • Gender        (e.g. male / female)\n\n"
            "Optional:\n"
            "  • Location      (e.g. Hyderabad / Warangal)\n"
            "  • Branch        (e.g. CSE / ECE / EEE)\n\n"
            "Example: 'I got rank 8000 OC male CSE Hyderabad'"
        )
        return PipelineResult(response=error_response, data=CollegeData())

    # ── Step 2: Run prediction ────────────────────────────────────────────────
    safe, moderate, dream = predict_colleges(
        rank        = user_data["rank"],
        category    = user_data["category"],
        gender      = user_data["gender"],
        location    = user_data["location"],
        branch_pref = user_data["preferred_branch"],
    )

    if safe.empty and moderate.empty and dream.empty:
        error_response = (
            "🚫 No colleges found for the given criteria.\n\n"
            "Suggestions:\n"
            "  • Try without a location filter\n"
            "  • Try without a branch preference\n"
            "  • Verify your category and gender spelling"
        )
        return PipelineResult(response=error_response, data=CollegeData())

    # ── Step 3: Format output ─────────────────────────────────────────────────
    lines = [
        "🎓  EAMCET College Prediction Results",
        _DIVIDER,
        f"  Rank     : {user_data['rank']}",
        f"  Category : {user_data['category']}",
        f"  Gender   : {user_data['gender']}",
        f"  Branch   : {user_data['preferred_branch']}",
        f"  Location : {user_data['location'] or 'All Telangana'}",
        _DIVIDER,
    ]

    def _section(emoji: str, label: str, df) -> list[str]:
        if df.empty:
            return []
        section = [f"\n{emoji}  {label} ({len(df)} college{'s' if len(df) > 1 else ''})\n"]
        for _, row in df.iterrows():
            section.append(f"  • {row['college_display']}")
            section.append(f"    Branch : {row['branch_code']}")
            section.append(f"    Score  : +{row['score']} ranks above cutoff\n")
        return section

    lines += _section("🟢", "SAFE — High Chance",     safe)
    lines += _section("🟡", "MODERATE — Good Chance", moderate)
    lines += _section("🔴", "DREAM — Lower Chance",   dream)

    lines += [
        _DIVIDER,
        "ℹ️   Based on previous year EAMCET cutoffs. Actual allotment may vary.",
    ]

    formatted_response = "\n".join(lines)

    # ── Step 4: Build CollegeData model ───────────────────────────────────────
    college_data = CollegeData(
        rank=user_data.get("rank"),
        category=user_data.get("category"),
        gender=user_data.get("gender"),
        branch=user_data.get("preferred_branch"),
        location=user_data.get("location"),
        safe=[row["college_display"] for _, row in safe.iterrows()] if not safe.empty else [],
        moderate=[row["college_display"] for _, row in moderate.iterrows()] if not moderate.empty else [],
        dream=[row["college_display"] for _, row in dream.iterrows()] if not dream.empty else [],
    )

    return PipelineResult(response=formatted_response, data=college_data)

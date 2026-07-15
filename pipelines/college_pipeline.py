"""
pipelines/college_pipeline.py
Handles the full college prediction flow:
  Extract → Predict → Build CollegeCard objects → Format output

Architecture
------------
* predict_colleges() is completely unchanged — returns (safe_df, moderate_df, dream_df).
* _build_college_card() maps each DataFrame row + metadata into a rich CollegeCard.
* The formatted text response string is preserved for backward compatibility.

Returns PipelineResult(response=str, data=CollegeData) where CollegeData now
carries list[CollegeCard] for safe / moderate / dream tiers.
"""

from __future__ import annotations

import re

import pandas as pd

from constants import DIVIDER
from agents.extractor_agent import extract_student_info
from tools.college_predictor import predict_colleges
from tools.metadata_loader import get_college_meta
from pipelines.pipeline_result import PipelineResult
from backend.models.response_models import CollegeCard, CollegeData
from backend.services.scoring_engine import (
    calculate_quality_score,
    calculate_roi_score,
    calculate_student_match_score,
    calculate_confidence,
    calculate_campus_rating,
    calculate_final_ranking
)
from backend.services.recommendation_engine import (
    generate_strengths,
    generate_weaknesses,
    generate_counselor_summary,
    generate_final_verdict
)
from backend.services.comparison_engine import build_comparison_payload

# ── Regex to parse "College Name (CODE)" produced by _clean_name() ──────────
_CODE_RE: re.Pattern[str] = re.compile(r"\((\w+)\)$")

# ── Tier labels shown on the card ───────────────────────────────────────────
_TIER_LABELS: dict[str, str] = {
    "SAFE":     "High Chance",
    "MODERATE": "Good Chance",
    "DREAM":    "Lower Chance",
}


# ── Card builder ─────────────────────────────────────────────────────────────

def _build_college_card(row: pd.Series, tier: str, user_data: dict) -> CollegeCard:
    """
    Convert one DataFrame row (from predict_colleges output) into a CollegeCard.
    """
    user_rank = user_data["rank"]
    branch_pref = user_data.get("preferred_branch", "NONE")
    college_display: str = row["college_display"]

    # Parse code from "Title Case Name (CODE)"
    m = _CODE_RE.search(college_display)
    code = m.group(1) if m else ""

    # Parse display name (strip " (CODE)" suffix)
    name_raw = college_display[: college_display.rfind("(")].strip()

    # Look up static enrichment metadata
    meta = get_college_meta(code)

    # Branches matched for this user (e.g. "CSE/CSM/CSD")
    predicted_branches = [
        b.strip() for b in str(row["branch_code"]).split("/") if b.strip()
    ]

    # score = cutoff_rank – user_rank  (positive means user is safely above cutoff)
    score: int = int(row["score"])
    closing_rank: int = user_rank + score   # last year's cutoff rank for this entry

    tier_label = _TIER_LABELS.get(tier, tier)

    if tier == "SAFE": prob = 95.0
    elif tier == "MODERATE": prob = 65.0
    else: prob = 30.0
    
    quality_score = calculate_quality_score(meta)
    roi_score, roi_label = calculate_roi_score(meta)
    match_score = calculate_student_match_score(meta, user_data, int(prob))
    confidence = calculate_confidence(meta, int(prob))
    campus_rating = calculate_campus_rating(meta)
    
    ranking = calculate_final_ranking(quality_score, prob, meta.get("popularity_score", 50.0))
    ranking_score = ranking["overall"]
    
    strengths = generate_strengths(meta)
    weaknesses = generate_weaknesses(meta)
    counselor_summary = generate_counselor_summary(meta, user_data)
    final_verdict = generate_final_verdict(meta, user_data, int(prob))
    
    comparison_ready = build_comparison_payload(meta, campus_rating, roi_score, match_score, quality_score)
    
    # Phase 10 Future-Proofing: Merge dicts instead of hardcoding all fields
    overrides = {
        "college_name": meta.get("display_name") or name_raw.title(),
        "college_code": code,
        "location": meta.get("location_display") or "Telangana",
        "predicted_branches": predicted_branches,
        "closing_rank": closing_rank,
        "score_above_cutoff": score,
        "admission_probability": tier,
        "recommendation_level": tier_label,
        "ranking_score": ranking_score,
        "ranking_breakdown": ranking,
        "student_match_score": match_score,
        "roi_score": roi_score,
        "roi_label": roi_label,
        "prediction_confidence": confidence,
        "campus_rating_stars": campus_rating,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "counselor_summary": counselor_summary,
        "comparison_ready": comparison_ready,
        "final_verdict": final_verdict,
        "medal_badge": None,
        "parent_summary": final_verdict  # Fallback for parent summary to final verdict
    }
    
    combined_data = {**meta, **overrides}
    
    # Filter out extra keys to prevent Pydantic extra_forbidden errors
    valid_keys = CollegeCard.model_fields.keys()
    filtered_data = {k: v for k, v in combined_data.items() if k in valid_keys}
    
    return CollegeCard(**filtered_data)


# ── Helper: build a list of CollegeCards from a tier DataFrame ───────────────

def _df_to_cards(df: pd.DataFrame, tier: str, user_data: dict) -> list[CollegeCard]:
    if df.empty:
        return []
    return [_build_college_card(row, tier, user_data) for _, row in df.iterrows()]

# ── Pipeline entry point ──────────────────────────────────────────────────────

def college_pipeline(query: str, **kwargs) -> PipelineResult:
    """
    Entry point for college prediction queries.
    """
    # Extract username for potential saved college functionality
    username = kwargs.get("username", "anonymous")
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

    user_rank: int = user_data["rank"]

    # ── Step 2: Run prediction ────────────────────────────────────────────────
    safe, moderate, dream = predict_colleges(
        rank=user_rank,
        category=user_data["category"],
        gender=user_data["gender"],
        location=user_data["location"],
        branch_pref=user_data["preferred_branch"],
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

    # ── Step 3: Build formatted text response (unchanged) ────────────────────
    lines = [
        "🎓  EAMCET College Prediction Results",
        DIVIDER,
        f"  Rank     : {user_rank}",
        f"  Category : {user_data['category']}",
        f"  Gender   : {user_data['gender']}",
        f"  Branch   : {user_data['preferred_branch']}",
        f"  Location : {user_data['location'] or 'All Telangana'}",
        DIVIDER,
    ]

    def _section(emoji: str, label: str, df: pd.DataFrame) -> list[str]:
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
        DIVIDER,
        "ℹ️   Based on previous year EAMCET cutoffs. Actual allotment may vary.",
    ]

    formatted_response = "\n".join(lines)

    # ── Step 4: Build structured CollegeCard objects ──────────────────────────
    safe_cards = _df_to_cards(safe, "SAFE", user_data)
    mod_cards = _df_to_cards(moderate, "MODERATE", user_data)
    dream_cards = _df_to_cards(dream, "DREAM", user_data)
    
    # Sort each tier by ranking_score descending
    safe_cards.sort(key=lambda x: x.ranking_score or 0, reverse=True)
    mod_cards.sort(key=lambda x: x.ranking_score or 0, reverse=True)
    dream_cards.sort(key=lambda x: x.ranking_score or 0, reverse=True)
    
    all_cards = safe_cards + mod_cards + dream_cards
    
    # Determine the global best match
    # Best Match if admission > 60% (Safe/Mod) AND overall score is highest among them
    eligible_for_best_match = [c for c in all_cards if c.admission_probability in ["SAFE", "MODERATE"]]
    if eligible_for_best_match:
        best = max(eligible_for_best_match, key=lambda x: x.ranking_score or 0)
        best.is_best_match = True
    elif all_cards: # Fallback to absolute best
        best = max(all_cards, key=lambda x: x.ranking_score or 0)
        best.is_best_match = True

    # Assign Medals and Rich Labels globally
    all_sorted_globally = sorted(all_cards, key=lambda x: x.ranking_score or 0, reverse=True)
    medals = ["🥇 #1 Recommendation", "🥈 #2 Recommendation", "🥉 #3 Recommendation"]
    
    for i, card in enumerate(all_sorted_globally):
        if i < 3:
            card.medal_badge = medals[i]
        elif card.is_best_match:
            card.medal_badge = "⭐ Best Match"
        elif card.placement_percentage and card.placement_percentage >= 90:
            card.medal_badge = "🎯 Highest Placement"
        elif card.avg_package_lpa and card.avg_package_lpa >= 6.0 and card.tuition_fee_per_year and card.tuition_fee_per_year <= 80000:
            card.medal_badge = "💰 Best ROI"
        elif card.ranking_score and card.ranking_score >= 80:
            card.medal_badge = "🏆 Premium Choice"
        else:
            card.medal_badge = None

    college_data = CollegeData(
        rank=user_rank,
        category=user_data.get("category"),
        gender=user_data.get("gender"),
        branch=user_data.get("preferred_branch"),
        location=user_data.get("location"),
        exam="EAMCET 2025",
        safe=safe_cards,
        moderate=mod_cards,
        dream=dream_cards,
    )

    return PipelineResult(response=formatted_response, data=college_data)

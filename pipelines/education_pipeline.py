"""
pipelines/education_pipeline.py  v5
Student-focused education pipeline.

Returns PipelineResult instead of plain strings to enable
structured data flow through the formatter layer.

Root cause of missing Definition section
-----------------------------------------
phi3:mini sometimes skips "SECTION 1 - DEFINITION:" and jumps straight
to key points, especially when the query contains the answer implicitly
("Explain DBMS" → model assumes definition IS the explanation).

Fix: Flatten to a single-pass prompt with LABELED LINES instead of
numbered sections. "DEFINITION:" on its own line is harder to skip than
"SECTION 1 - DEFINITION:" because there's no numbering to confuse the model.
Also: fallback parser now captures unlabeled leading text as definition.
"""

from constants import DIVIDER
from utils.logger import get_logger
import re

from backend.providers.provider_factory import get_provider
from utils.complexity   import detect_complexity
from utils.section_parser import parse_sections
from utils.text_cleaner import clean_text
from typing import final
from pipelines.pipeline_result import PipelineResult
from schemas.education_schema import EDUCATION_LABELS
from backend.models.response_models import EducationData

logger = get_logger(__name__)
_TOKEN_CAP :final = {"low": 400, "medium": 1200, "high": 1200}

_SYSTEM = (
    "You are an experienced computer science professor.\n"
    "Write detailed, factual, and exam-oriented answers suitable for B.Tech students.\n"
    "No filler phrases.\n"
    "No markdown.\n"
    "No bold.\n"
    "Plain English.\n"
    "Use bullet points when appropriate.\n"
    "Write thorough, long answers. Do not skip any section requested in the prompt.\n"
)

_SECTION_LABELS :final = {
    "definition": ["DEFINITION"],
    "keypoints": [
        "KEY POINTS",
        "POINTS",
        "FEATURES",
        "CHARACTERISTICS",
        "ADVANTAGES",
        "DIFFERENCES",
    ],
    "working": ["WORKING", "PRINCIPLE", "PRINCIPLES", "HOW IT WORKS"],
    "advantages": ["ADVANTAGES", "ADVANTAGE", "PROS", "BENEFITS"],
    "disadvantages": ["DISADVANTAGES", "DISADVANTAGE", "CONS", "DRAWBACKS"],
    "applications": ["APPLICATIONS", "APPLICATION", "USES", "USE CASES"],
    "example": ["EXAMPLE"],
    "examtip": ["EXAM TIP"],
    "diagram": [
        "DIAGRAM",
        "FLOW CHART",
        "FLOWCHART",
        "BLOCK DIAGRAM",
    ],
    "summary": ["SUMMARY", "CONCLUSION"],
}

_BULLET_PATTERN = re.compile(r"^[\-\*\u2022].+", re.MULTILINE)

_HEADER = f"{DIVIDER}\n📚  EDUCATION ASSISTANT\n{DIVIDER}\n\n"


def _build_prompt(query: str, level: str) -> str:
    """
    Single-label prompt format — more reliable than numbered sections
    for small models. Each label is a standalone line keyword the model
    must echo before writing content.
    """
    base = (
        f"Topic: {query}\n\n"
        "Write your answer using EXACTLY these labels on their own lines:\n\n"
        "DEFINITION:\n"
        "(define the topic in 2 sentences)\n\n"
        "KEY POINTS:\n"
        "(3-5 bullet points starting with -)\n\n"
        "WORKING:\n"
        "(explain how it works or its core principles)\n\n"
    )
    if level in ("medium", "high"):
        base += (
            "ADVANTAGES:\n"
            "(list advantages or benefits)\n\n"
            "DISADVANTAGES:\n"
            "(list disadvantages or drawbacks)\n\n"
            "APPLICATIONS:\n"
            "(list real-world applications)\n\n"
            "EXAMPLE:\n"
            "(one real-world example in 1-2 sentences)\n\n"
            "EXAM TIP:\n"
            "(one commonly tested fact or question pattern)\n\n"
        )

    if level == "high":
        base += (
            "DIAGRAM:\n"
            "(simple flow or block representation if applicable)\n\n"
        )

    base += (
        "SUMMARY:\n"
        "(1-2 sentence summary)\n\n"
        "Do NOT use bold, headers, or markdown. Keep every section brief."
    )
    return base


def education_pipeline(query: str, **kwargs) -> PipelineResult:
    """
    Entry point for education queries.
    Returns structured education data alongside formatted display string.
    """
    level = detect_complexity(query)

    prompt    = _build_prompt(query, level)
    token_cap = _TOKEN_CAP[level]
    logger.info("Education pipeline: complexity=%s  tokens=%d", level, token_cap)

    try:
        provider = get_provider("education")
        result = provider.generate(prompt=prompt, system=_SYSTEM)
        raw = result.content
        if not raw:
            raise RuntimeError("LLM returned an empty response")
    except Exception as exc:
        logger.error("Education pipeline error: %s", exc, exc_info=True)
        error_response = f"⚠️  LLM unavailable.\nError: {exc}"
        return PipelineResult(
            response=error_response,
            data=EducationData(topic=query, title=query)
        )

    raw = clean_text(raw)
    secs = parse_sections(
        raw,
        _SECTION_LABELS,
        capture_leading_text=True,
    )

    if secs["definition"] and not secs["keypoints"]:
        bullets = _BULLET_PATTERN.findall(raw)
        if bullets:
            secs["keypoints"] = "\n".join(bullets)

    if not any(secs.values()):
        secs["definition"] = raw

    out = [_HEADER]

    if secs["definition"]:
        out += ["", "📖  Definition", secs["definition"]]

    if secs["keypoints"]:
        out += ["", f"{DIVIDER}", "🔑  Key Points", secs["keypoints"]]

    if secs.get("working"):
        out += ["", f"{DIVIDER}", "⚙️  Working", secs["working"]]

    if secs.get("advantages"):
        out += ["", f"{DIVIDER}", "✅  Advantages", secs["advantages"]]

    if secs.get("disadvantages"):
        out += ["", f"{DIVIDER}", "❌  Disadvantages", secs["disadvantages"]]

    if secs.get("applications"):
        out += ["", f"{DIVIDER}", "🚀  Applications", secs["applications"]]

    if secs["example"]:
        out += ["", f"{DIVIDER}", "💡  Example", secs["example"]]

    if secs["examtip"]:
        out += ["", f"{DIVIDER}", "🎯  Exam Tip", secs["examtip"]]

    if secs["diagram"]:
        out += [
            "",
            f"{DIVIDER}",
            "🖼 Diagram Hint",
            secs["diagram"],
        ]

    if secs.get("summary"):
        out += ["", f"{DIVIDER}", "📝  Summary", secs["summary"]]

    out.append(f"\n{DIVIDER}")
    formatted_response = "\n".join(out)

    education_data = EducationData(
        topic=query,
        definition=secs.get("definition", "").strip() or None,
        key_points=secs.get("keypoints", "").strip() or None,
        working=secs.get("working", "").strip() or None,
        advantages=secs.get("advantages", "").strip() or None,
        disadvantages=secs.get("disadvantages", "").strip() or None,
        applications=secs.get("applications", "").strip() or None,
        example=secs.get("example", "").strip() or None,
        exam_tip=secs.get("examtip", "").strip() or None,
        summary=secs.get("summary", "").strip() or None,
        title=query,
        explanation=secs.get("definition", "").strip() or None,
        key_formulas=[secs.get("keypoints", "").strip()] if secs.get("keypoints", "").strip() else None,
        tips=[secs.get("examtip", "").strip()] if secs.get("examtip", "").strip() else None,
    )

    return PipelineResult(response=formatted_response, data=education_data)

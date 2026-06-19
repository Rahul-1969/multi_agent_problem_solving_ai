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

from llm.ollama_client import call_llm
from utils.complexity   import detect_complexity
from utils.section_parser import parse_sections
from utils.text_cleaner import clean_text
from typing import final
from pipelines.pipeline_result import PipelineResult
from schemas.education_schema import EDUCATION_LABELS
from backend.models.response_models import EducationData

logger = get_logger(__name__)
_TOKEN_CAP :final = {"low": 250, "medium": 350, "high": 500}

_SYSTEM = (
    "You are an experienced computer science professor.\n"
    "Write factual and exam-oriented answers.\n"
    "No filler phrases.\n"
    "No markdown.\n"
    "No bold.\n"
    "Plain English.\n"
    "Keep sections short.\n"
    "Always provide a definition.\n"
    "Always provide key points.\n"
    "Use bullet points when appropriate.\n"
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
    "example": ["EXAMPLE"],
    "examtip": ["EXAM TIP"],
    "diagram": [
        "DIAGRAM",
        "FLOW CHART",
        "FLOWCHART",
        "BLOCK DIAGRAM",
    ],
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
        "(3 bullet points starting with -)\n\n"
    )
    if level in ("medium", "high"):
        base += (
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
    base += "Do NOT use bold, headers, or markdown. Keep every section brief."
    return base


def education_pipeline(query: str) -> PipelineResult:
    """
    Entry point for education queries.
    Returns structured education data alongside formatted display string.
    """
    level = detect_complexity(query)

    prompt    = _build_prompt(query, level)
    token_cap = _TOKEN_CAP[level]
    logger.info("Education pipeline: complexity=%s  tokens=%d", level, token_cap)

    try:
        raw = call_llm(prompt=prompt, system=_SYSTEM, num_predict=token_cap)
    except RuntimeError as exc:
        logger.error("Education pipeline error: %s", exc)
        error_response = f"⚠️  LLM unavailable.\nError: {exc}"
        return PipelineResult(
            response=error_response,
            data=EducationData(topic=query)
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

    if secs["example"]:
        out += ["", f"{DIVIDER}", "💡  Example", secs["example"]]

    if secs["examtip"]:
        out += ["", f"{DIVIDER}", "🎯  Exam Tip", secs["examtip"]]

    if secs["diagram"]:
        out += [
            "",
            f"{DIVIDER}",
            "🖼 Diagram Hint",
            secs["diagram"]
        ]

    out.append(f"\n{DIVIDER}")
    formatted_response = "\n".join(out)

    # Parse formatted response into EducationData model
    parsed_sections = parse_sections(formatted_response, EDUCATION_LABELS)

    education_data = EducationData(
        topic=query,
        definition=parsed_sections.get("definition", "").strip() or None,
        key_points=parsed_sections.get("key_points", "").strip() or None,
        example=parsed_sections.get("example", "").strip() or None,
        exam_tip=parsed_sections.get("exam_tip", "").strip() or None,
    )

    return PipelineResult(response=formatted_response, data=education_data)

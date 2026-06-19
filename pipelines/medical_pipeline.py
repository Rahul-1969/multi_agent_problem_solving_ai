"""
pipelines/medical_pipeline.py  v7

Returns PipelineResult instead of plain strings to enable
structured data flow through the formatter layer.

Changes in this version
------------------------
1. DIAGNOSIS-FOCUSED prompt — explicitly tells Phi3 to return
   "possible diagnoses/causes", NOT symptom names.
   Fixes: "chest pain → chest pain" (symptom repeated as diagnosis).

2. TOKEN CAP raised 500 → 600 — prevents lifestyle section truncation.
   Fixes: "Darkness aids" / "including immune" mid-sentence cuts.

3. Uses clean_text() from utils.text_cleaner.

4. Medical diagnosis prompt improved:
   "List possible medical DIAGNOSES or CONDITIONS that could CAUSE
   these symptoms" — makes Phi3 give actual condition names.
"""

from utils.logger import get_logger
import re
from typing import Final

from constants import DIVIDER
from llm.ollama_client  import call_llm
from utils.section_parser import parse_sections
from utils.text_cleaner import clean_text
from pipelines.pipeline_result import PipelineResult
from schemas.medical_schema import MEDICAL_LABELS
from backend.models.response_models import MedicalData

logger = get_logger(__name__)

_DISCLAIMER = (
    "\n⚠️  IMPORTANT DISCLAIMER\n"
    "This is AI-generated information only, NOT medical advice.\n"
    "Please consult a qualified healthcare provider."
)

_SYSTEM = (
    "You are a general health information assistant. "
    "RULES YOU MUST FOLLOW:\n"
    "1. List possible DIAGNOSES or CONDITIONS that CAUSE the symptoms — "
    "do NOT repeat the symptoms themselves as conditions.\n"
    "2. Always list the MOST COMMON conditions first "
    "(cold, flu, dehydration, muscle strain, GERD) before rare ones.\n"
    "3. NEVER recommend prescription medications, cardiac drugs, "
    "nitroglycerin, opioids, antibiotics, or emergency medications.\n"
    "4. Only suggest: paracetamol, ibuprofen, rest, fluids, "
    "saline spray, lozenges, warm compress.\n"
    "5. Plain text only. No markdown. No bold. Short sentences."
)

_UNSAFE_DRUGS = [
    (r'\bnitroglycerin\b',  'consult a cardiologist'),
    (r'\bwarfarin\b',       'consult your doctor'),
    (r'\bmetformin\b',      'consult your doctor'),
    (r'\bamoxicillin\b',    'consult your doctor for antibiotics'),
    (r'\bpenicillin\b',     'consult your doctor for antibiotics'),
    (r'\bmorphine\b',       'seek emergency care'),
    (r'\bcodeine\b',        'consult your doctor'),
    (r'\blisinopril\b',     'consult your doctor'),
    (r'\bstatins?\b',       'consult your doctor'),
]

_HIGH_RISK_PATTERNS = [
    ("chest pain", "left arm"),
    ("chest pain", "shortness of breath"),

    "difficulty breathing",
    "shortness of breath",
    "trouble breathing",
    "can't breathe",
    "loss of consciousness",
    "fainted",
    "slurred speech",
    "face drooping",
    "vomiting blood",
    "severe bleeding",
]

_TOKEN_CAP = 600

_SECTION_LABELS: Final = {
    "conditions": [
        "CONDITIONS",
        "POSSIBLE CONDITIONS",
        "DIAGNOSES",
        "DIAGNOSIS",
        "CAUSES",
    ],
    "treatments": [
        "TREATMENTS",
        "TREATMENT",
        "REMEDIES",
        "SAFE TREATMENTS",
    ],
    "lifestyle": [
        "LIFESTYLE",
        "LIFESTYLE & PRECAUTIONS",
        "PRECAUTIONS",
        "SELF CARE",
    ],
    "emergency": [
        "EMERGENCY",
        "WARNING SIGNS",
        "RED FLAGS",
        "WHEN TO SEEK HELP",
    ],
}


def _is_emergency(query: str) -> bool:
    q = query.lower()

    for pattern in _HIGH_RISK_PATTERNS:

        if isinstance(pattern, str):
            if pattern in q:
                return True

        else:
            if all(p in q for p in pattern):
                return True

    return False


def _apply_safety_filter(text: str) -> str:
    for pattern, replacement in _UNSAFE_DRUGS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def _sec(text: str) -> str:
    return text if text else "(not available)"


def medical_pipeline(query: str) -> PipelineResult:
    """
    Entry point for medical queries.
    Returns structured medical data alongside formatted display string.
    """
    # Emergency bypass — immediate warning without LLM
    if _is_emergency(query):
        emergency_response = (
            f"🚨  MEDICAL EMERGENCY WARNING\n{DIVIDER}\n\n"
            "Your symptoms may indicate a serious medical emergency.\n\n"
            "Call emergency services or go to the nearest emergency room immediately.\n\n"
            "Do NOT rely on this AI for emergency medical guidance."
            + _DISCLAIMER
        )
        return PipelineResult(
            response=emergency_response,
            data=MedicalData(emergency="EMERGENCY - Seek immediate medical attention")
        )

    prompt = (
        f"Patient symptoms: {query}\n\n"
        "Answer using EXACTLY these labels on their own lines:\n\n"
        "CONDITIONS:\n"
        "(List up to 3 possible DIAGNOSES or medical CONDITIONS that "
        "could CAUSE these symptoms. Do NOT repeat the symptoms as conditions. "
        "Format: Condition Name - Likelihood: High/Moderate/Low - "
        "Reason: why this condition causes the symptom)\n\n"
        "TREATMENTS:\n"
        "(Safe OTC remedies only — paracetamol, ibuprofen, rest, fluids. "
        "No prescription drugs. When to see a doctor.)\n\n"
        "LIFESTYLE:\n"
        "(Exactly 3 complete tips on diet, rest, and hydration. "
        "Finish each tip fully before moving to the next.)\n\n"
        "EMERGENCY:\n"
        "(1-2 lines: specific warning signs needing immediate medical care)\n\n"
        "Plain text only. Keep each section brief."
    )

    try:
        logger.info("Medical pipeline: single LLM call")
        raw = call_llm(prompt=prompt, system=_SYSTEM, num_predict=_TOKEN_CAP)
        raw = clean_text(raw, remove_filler=True)
        raw = _apply_safety_filter(raw)
    except RuntimeError as exc:
        logger.error("Medical pipeline error: %s", exc)
        error_response = f"⚠️  LLM unavailable.\nError: {exc}"
        return PipelineResult(
            response=error_response,
            data=MedicalData()
        )

    sections = parse_sections(raw, _SECTION_LABELS)

    conditions = sections["conditions"]
    treatments = sections["treatments"]
    lifestyle = sections["lifestyle"]
    emergency = sections["emergency"]

    if not any((conditions, treatments, lifestyle)):
        logger.warning("Medical: labels skipped — raw output")
        fallback_response = f"🩺  MEDICAL INFORMATION\n{DIVIDER}\n\n{raw.strip()}{_DISCLAIMER}"
        return PipelineResult(
            response=fallback_response,
            data=MedicalData()
        )

    lines = [
        f"🩺  MEDICAL INFORMATION\n{DIVIDER}\n",
        f"📋  Possible Conditions (most common first)\n{_sec(conditions)}\n",
        f"{DIVIDER}\n",
        f"💊  Safe Treatments\n{_sec(treatments)}\n",
        f"{DIVIDER}\n",
        f"🥗  Lifestyle & Precautions\n{_sec(lifestyle)}\n",
    ]
    if emergency:
        lines += [f"{DIVIDER}\n", f"🚨  Seek Immediate Medical Attention If\n{emergency}\n"]

    lines.append(_DISCLAIMER)
    formatted_response = "\n".join(lines)

    # Parse formatted response into MedicalData model
    parsed_sections = parse_sections(formatted_response, MEDICAL_LABELS)

    medical_data = MedicalData(
        conditions=parsed_sections.get("conditions", "").strip() or None,
        treatments=parsed_sections.get("treatments", "").strip() or None,
        lifestyle=parsed_sections.get("lifestyle", "").strip() or None,
        emergency=parsed_sections.get("emergency", "").strip() or None,
    )

    return PipelineResult(response=formatted_response, data=medical_data)

"""
pipelines/coding_pipeline.py
Handles coding and programming queries.

Returns PipelineResult instead of plain strings to enable
structured data flow through the formatter layer.

Fixes in this version
----------------------
1. _clean_code_output now strips headers (###) in addition to bold (**)
2. Language detection extended: c#, typescript, go, rust, kotlin
3. Uses clean_text() from utils.text_cleaner (centralised)
4. Explanation/complexity extraction fixed — divider line no longer
   bleeds into explanation field
"""

from utils.logger import get_logger
import re
from difflib import get_close_matches
from typing import Final

from constants import DIVIDER
from llm.ollama_client       import call_llm
from utils.complexity        import detect_complexity
from utils.known_algorithms  import KNOWN_ALGORITHMS
from utils.section_parser    import parse_sections
from utils.text_cleaner      import clean_text
from pipelines.pipeline_result import PipelineResult
from schemas.coding_schema import CODING_LABELS
from backend.models.response_models import CodingData

logger = get_logger(__name__)

# Missing pattern that caused runtime NameError (see audit P0-4)
_CODE_PATTERN = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)

_SYSTEM = (
    "You are a senior software engineer.\n"
    "Always provide complete working code.\n"
    "Finish the entire code before writing any explanation.\n"
    "Always provide a brief explanation even if the user does not ask for one.\n"
    "Always provide time and space complexity.\n"
    "For complex problems, add one important edge case or optimization tip.\n"
    "Keep explanations concise.\n"
    "No verbose introductions.\n"
)
# Section labels for shared parser (order matters for leading-text capture)
_SECTION_LABELS: Final[dict[str, list[str]]] = {
    "code": [
        "CODE",
        "PROGRAM",
        "IMPLEMENTATION",
    ],
    "explanation": [
        "EXPLANATION",
        "DESCRIPTION",
    ],
    "complexity": [
        "COMPLEXITY",
        "TIME COMPLEXITY",
        "SPACE COMPLEXITY",
    ],
    "tip": [
        "EDGE CASE",
        "OPTIMIZATION",
        "TIP",
    ],
}

# ── Language detection ────────────────────────────────────────────────────────
_LANG_MAP = {
    "java":       "java",
    "c++":        "cpp",
    "cpp":        "cpp",
    "javascript": "javascript",
    "typescript": "typescript",
    "c#":         "csharp",
    "golang":     "go",
    "go ":        "go",
    "rust":       "rust",
    "kotlin":     "kotlin",
    "python":     "python",
    " go ": "go",
}

def _detect_language(query: str) -> str:
    q = query.lower()
    for keyword, lang in _LANG_MAP.items():
        if keyword in q:
            return lang
    return "python"   # default


def _build_prompt(query: str, level: str) -> str:
    # Force labeled sections on their own lines to aid robust parsing
    prompt = (
        f"{query}\n\n"
        "Answer using EXACTLY these labels on their own lines:\n\n"
        "CODE:\n"
        "(Provide complete working code; finish all lines before any explanation)\n\n"
        "EXPLANATION:\n"
        "(2-3 sentence brief explanation)\n\n"
        "COMPLEXITY:\n"
        "(Time complexity and space complexity)\n\n"
    )

    if level == "high":
        prompt += (
            "TIP:\n"
            "(One important edge case or optimization)\n\n"
        )

    prompt += "Plain text only. No markdown. No bold."
    return prompt


def _clean_code_output(raw: str, lang: str) -> str:
    """
    Normalise LLM code output into consistent ```lang\ncode\n``` format.
    Strips bold, headers, and divider lines from explanation section.
    """
    raw = raw.strip()
    # Try extracting fenced code block first (models often emit fenced code)
    fence = re.search(r'```(?P<fence_lang>\w+)?\s*\n(?P<code>.*?)```', raw, re.DOTALL | re.IGNORECASE)

    if fence:
        detected_lang = fence.group("fence_lang") or lang
        code = fence.group("code").strip()
        after_raw = raw[fence.end():].strip()
        # Remove divider lines from the trailing text
        after_raw = re.sub(r'^─+$', '', after_raw, flags=re.MULTILINE).strip()

        # Parse labeled sections from the trailing text
        after_sections = parse_sections(after_raw, _SECTION_LABELS)
        parts: list[str] = []
        explanation = after_sections.get("explanation", "")
        complexity = after_sections.get("complexity", "")
        tip = after_sections.get("tip", "")

        if explanation:
            parts.append(clean_text(explanation, remove_filler=True))
        if complexity:
            parts.append(clean_text(complexity, remove_filler=True))
        if tip:
            parts.append(clean_text(tip, remove_filler=True))

        if parts:
            return f"```{detected_lang}\n{code}\n```\n\n{'\n\n'.join(parts)}"
        return f"```{detected_lang}\n{code}\n```"

    # No fence — use shared parser to extract sections (capture leading text as code)
    sections = parse_sections(raw, _SECTION_LABELS, capture_leading_text=True)
    code = sections.get("code", "").strip()
    explanation = sections.get("explanation", "").strip()
    complexity = sections.get("complexity", "").strip()
    tip = sections.get("tip", "").strip()

    parts = []
    if explanation:
        parts.append(clean_text(explanation, remove_filler=True))
    if complexity:
        parts.append(clean_text(complexity, remove_filler=True))
    if tip:
        parts.append(clean_text(tip, remove_filler=True))

    if code:
        if parts:
            return f"```{lang}\n{code}\n```\n\n{'\n\n'.join(parts)}"
        return f"```{lang}\n{code}\n```"

    # Fallback: treat entire raw as code block
    return f"```{lang}\n{raw}\n```"


def validate_coding_query(query: str) -> str | None:
    """
    Only validate algorithm/DSA requests.
    Returns clarification message if unknown, None if valid.
    """
    q = query.lower().strip()

    trigger_words = (
        "binary search", "linear search", "jump search",
        "interpolation search", "fibonacci search",
        "bubble sort", "selection sort", "insertion sort",
        "merge sort", "quick sort", "heap sort",
        "counting sort", "radix sort", "shell sort",
        "algorithm", "dfs", "bfs",
        "tree traversal", "graph traversal",
        "linked list", "stack", "queue", "bst", "avl", "heap",
    )

    if not any(word in q for word in trigger_words):
        return None   # not an algorithm query — pass through

    if any(algo in q for algo in KNOWN_ALGORITHMS):
        return None   # known valid algorithm

    # Strip common prefixes to isolate algorithm name
    candidate = q
    for prefix in (
        "write a python program for", "write a java program for",
        "write a c program for", "write a cpp program for",
        "write code for", "write code to", "write program for",
        "write a program for", "write a program to",
        "program for", "program to", "implement",
        "code for", "code to", "python program for",
    ):
        if candidate.startswith(prefix):
            candidate = candidate[len(prefix):].strip()
            break

    suggestions = get_close_matches(
        candidate, list(KNOWN_ALGORITHMS), n=3, cutoff=0.35
    )

    if suggestions:
        return (
            "Algorithm not recognized.\n\n"
            "Did you mean:\n"
            + "\n".join(f"• {s.title()}" for s in suggestions)
        )

    return (
        "Algorithm not recognized.\n\n"
        "Please check the algorithm name or provide more details."
    )


def coding_pipeline(query: str) -> PipelineResult:
    """
    Entry point for coding queries.
    Returns structured coding data alongside formatted display string.
    """
    level = detect_complexity(query)
    token_cap = {
        "low": 400,
        "medium": 550,
        "high": 800
    }[level]
    lang      = _detect_language(query)
    logger.info("Coding pipeline: complexity=%s  lang=%s  tokens=%d",
                level, lang, token_cap)

    # Validation check (only for DSA/algorithm queries)
    validation_msg = validate_coding_query(query)
    if validation_msg:
        validation_response = f"💻  CODING ASSISTANT\n{DIVIDER}\n\n{validation_msg}\n\n{DIVIDER}"
        return PipelineResult(
            response=validation_response,
            data=CodingData(
                language=lang,
                clarification=validation_msg.split("\n")
            )
        )

    prompt = _build_prompt(query, level)

    try:
        raw = call_llm(prompt=prompt, system=_SYSTEM, num_predict=token_cap)
    except RuntimeError as exc:
        logger.error("Coding pipeline error: %s", exc)
        error_response = f"⚠️  LLM unavailable.\nError: {exc}"
        return PipelineResult(
            response=error_response,
            data=CodingData(language=lang)
        )

    cleaned = _clean_code_output(raw, lang)
    formatted_response = f"💻  CODING ASSISTANT\n{DIVIDER}\n\n{cleaned}\n\n{DIVIDER}"

    # Parse formatted response into CodingData model
    # Extract code block from the cleaned output
    code_match = _CODE_PATTERN.search(cleaned)
    if code_match:
        code_language = code_match.group(1) or lang
        code_content = code_match.group(2).strip()
        after_code = cleaned[code_match.end():].strip()
        parsed_sections = parse_sections(after_code, CODING_LABELS)
        explanation = parsed_sections.get("explanation", "").strip() or None
        complexity = parsed_sections.get("complexity", "").strip() or None
        tip = parsed_sections.get("tip", "").strip() or None
    else:
        code_language = lang
        code_content = None
        explanation = cleaned.strip() or None
        complexity = None
        tip = None

    coding_data = CodingData(
        language=code_language,
        code=code_content,
        explanation=explanation,
        complexity=complexity,
        tip=tip,
    )

    return PipelineResult(response=formatted_response, data=coding_data)

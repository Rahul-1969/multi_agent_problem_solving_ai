"""
utils/text_cleaner.py
Centralised text cleaning utility.

Replaces repeated re.sub() calls scattered across:
- general_pipeline.py
- coding_pipeline.py
- medical_pipeline.py
- education_pipeline.py
- base_agent.py / refiner_agent.py

Single import: from utils.text_cleaner import clean_text
"""

import re

# Compiled once at import time — no per-call recompilation
_BOLD_RE     = re.compile(r'\*{1,3}')
_HEADER_RE   = re.compile(r'#{1,6}\s*')
_FILLER_RE   = re.compile(
    r'\b(essentially|basically|certainly|absolutely|'
    r'it is important to note that|'
    r"it's important to note that|"
    r'in essence,?\s*|in other words,?\s*|'
    r'to summarize,?\s*|to put it simply,?\s*|'
    r'as you can see,?\s*|'
    r'great question[!.]?\s*|'
    r'certainly[!,]?\s*|'
    r'of course[!,]?\s*)\s*',
    re.IGNORECASE
)
_MULTI_NL_RE = re.compile(r'\n{3,}')


def clean_text(text: str, remove_filler: bool = True) -> str:
    """
    Remove markdown bold, headers, optional filler phrases, and
    collapse excessive blank lines.

    Args:
        text          : raw LLM output
        remove_filler : strip AI filler phrases (default True)
    """
    text = _BOLD_RE.sub('', text)
    text = _HEADER_RE.sub('', text)
    if remove_filler:
        text = _FILLER_RE.sub('', text)
    text = _MULTI_NL_RE.sub('\n\n', text)
    return text.strip()

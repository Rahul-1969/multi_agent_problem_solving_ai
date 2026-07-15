import re
import os
from backend.providers.provider_factory import get_provider
from backend.observability.metrics import metrics
from utils.prompt_loader import load_prompt

# Stage 1: Fast Rule Filter
LIVE_TRIGGERS = [
    r"\b(latest|today|current|now|2025|2026)\b",
    r"\b(news|trending|recent|just announced)\b",
    r"\b(still|has .+ become|is .+ now)\b",
    r"\b(top colleges? \d{4})\b",
    r"\b(naac (result|update|grade change))\b",
    r"\b(placement (package|company|trend) \d{4})\b",
]

LOCAL_TRIGGERS = [
    r"^\s*(hi|hello|hey|thanks|thank you|ok|okay)\s*$",
    r"\b(explain|what is|define|how does|difference between)\b",
    r"\b(write|implement|code|algorithm|sort|search)\b",
    r"\b(predict|rank \d+|eamcet|cutoff)\b",
]

LIVE_REGEX = [re.compile(p, re.IGNORECASE) for p in LIVE_TRIGGERS]
LOCAL_REGEX = [re.compile(p, re.IGNORECASE) for p in LOCAL_TRIGGERS]

def _rule_filter(query: str) -> str | None:
    for regex in LOCAL_REGEX:
        if regex.search(query):
            # Let the fine-grained scorer in domain_router handle it by returning 'local'
            return "local"
            
    for regex in LIVE_REGEX:
        if regex.search(query):
            return "live"
            
    return None

def classify_intent(query: str) -> str:
    """
    Returns (intent) using Fast Rule Filter first, then LLM fallback.
    Records metrics for method used.
    """
    # 1. Fast Rule Filter
    intent = _rule_filter(query)
    if intent:
        metrics.record_classifier("rule", intent)
        return intent

    # 2. LLM Fallback (Ambiguous)
    template = load_prompt("classifier_prompt.txt")
    prompt = template.format(query=query)
    provider = get_provider("classify")
    
    intent = provider.classify(prompt)
    
    # Valid intents mapping
    valid_intents = ["local", "live", "college", "coding", "medical", "education", "career", "scholarship"]
    
    # Simple extraction
    extracted_intent = "local" # default
    for vi in valid_intents:
        if vi in intent:
            extracted_intent = vi
            break
            
    metrics.record_classifier("llm", extracted_intent)
    return extracted_intent

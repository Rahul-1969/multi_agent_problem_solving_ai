import os

ENABLE_GEMINI           = os.getenv("ENABLE_GEMINI", "true").lower() == "true"
ENABLE_CHAT_TITLES      = os.getenv("ENABLE_CHAT_TITLES", "true").lower() == "true"
ENABLE_LIVE_PIPELINE    = os.getenv("ENABLE_LIVE_PIPELINE", "true").lower() == "true"
ENABLE_CAREER_PIPELINE  = os.getenv("ENABLE_CAREER_PIPELINE", "true").lower() == "true"
ENABLE_SCHOLARSHIP_PIPELINE = os.getenv("ENABLE_SCHOLARSHIP_PIPELINE", "true").lower() == "true"
ENABLE_COLLEGE_ENRICH   = os.getenv("ENABLE_COLLEGE_ENRICH", "false").lower() == "true"
ENABLE_CAREER_GUIDANCE  = os.getenv("ENABLE_CAREER_GUIDANCE", "false").lower() == "true"
ENABLE_GROUNDING        = os.getenv("ENABLE_GROUNDING", "true").lower() == "true"
ENABLE_OBSERVABILITY    = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"

FLASH_DAILY_LIMIT       = int(os.getenv("FLASH_DAILY_LIMIT", "50"))
PRO_DAILY_LIMIT         = int(os.getenv("PRO_DAILY_LIMIT", "5"))

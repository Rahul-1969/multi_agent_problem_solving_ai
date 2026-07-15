GEMINI_FLASH_MODEL  = "gemini-2.5-flash"
GEMINI_PRO_MODEL    = "gemini-2.5-pro"

CACHE_TTL_SECONDS   = 1800          # 30 minutes
METADATA_CACHE_TTL  = 86400         # 24 hours
BATCH_SIZE          = 10

CONFIDENCE_THRESHOLDS = {
    "avg_package_lpa":     {"max_change_pct": 0.40},
    "highest_package_lpa": {"max_change_pct": 0.50},
    "naac_grade":          {"allowed": ["A++", "A+", "A", "B++", "B+", "B", "C"]},
    "nirf_rank":           {"min": 1, "max": 2000},
    "placement_pct":       {"min": 0, "max": 100},
    "official_website":    {"check_alive": True},
}

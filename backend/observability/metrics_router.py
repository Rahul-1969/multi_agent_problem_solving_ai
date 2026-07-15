from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend.observability.metrics import metrics

# Create a router for metrics
router = APIRouter(prefix="/admin", tags=["Admin"])

# Optionally add a simple dependency to check for an admin token
# For now, this is just open, but can be protected.
def verify_admin():
    # In production, verify a JWT or admin token here
    pass

@router.get("/metrics", response_model=Dict[str, Any])
def get_metrics(admin: None = Depends(verify_admin)):
    """
    Get observability metrics including Gemini usage, cache hits, 
    and classifier accuracy.
    """
    return metrics.get_summary()

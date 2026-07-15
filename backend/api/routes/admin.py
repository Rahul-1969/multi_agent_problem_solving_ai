from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
import os
import psutil
from backend.observability.metrics import metrics
from backend.cache.usage_tracker import usage_tracker
from backend.cache.gemini_cache import gemini_cache
from backend.providers.provider_factory import get_provider_status
from tools.metadata_loader import load_college_metadata, load_scholarship_metadata
from backend.auth.auth_dependency import get_current_user
from backend.auth.token_models import TokenPayload
from utils.logger import get_logger

logger = get_logger(__name__)

# Admin configuration from environment
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_USERS = os.getenv("ADMIN_USERS", "")

# Parse comma-separated admin users list
_admin_users_list: list[str] = []
if ADMIN_USERS:
    _admin_users_list = [u.strip() for u in ADMIN_USERS.split(",") if u.strip()]

# Startup check: warn if no admin credentials configured
if not ADMIN_USERNAME and not ADMIN_USERS:
    logger.warning(
        "Admin endpoints unavailable: neither ADMIN_USERNAME nor ADMIN_USERS environment variables are set. "
        "Admin routes will return 503 until configured."
    )


def _is_admin_user(username: str) -> bool:
    """Check if a username has admin privileges."""
    if username == ADMIN_USERNAME:
        return True
    if username in _admin_users_list:
        return True
    return False


async def verify_admin(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """
    FastAPI dependency that verifies the current user has admin privileges.

    Uses get_current_user for authentication, then checks if the username
    matches ADMIN_USERNAME or is in the ADMIN_USERS list.

    Raises:
        HTTPException 403: If user is authenticated but not an admin
        HTTPException 503: If no admin credentials are configured
    """
    # If no admin credentials configured, deny access with 503
    if not ADMIN_USERNAME and not ADMIN_USERS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin endpoint unavailable: no admin credentials configured",
        )

    if not _is_admin_user(current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


router = APIRouter(prefix="/api/v1/admin", tags=["Admin Dashboard"])

@router.get("/overview")
async def get_overview(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns high-level system overview hooked into observability metrics.
    """
    summary = metrics.get_summary()
    return {
        "status": "success",
        "data": {
            "api_metrics": summary,
            "system_health": "healthy"
        }
    }

@router.get("/providers")
async def get_providers(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns AI provider status.
    """
    status = get_provider_status()
    usage = usage_tracker.get_stats()
    return {
        "status": "success",
        "data": {
            "provider_status": status,
            "usage_stats": usage
        }
    }

@router.get("/cache")
async def get_cache(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns Gemini cache statistics.
    """
    stats = gemini_cache.get_stats()
    return {
        "status": "success",
        "data": stats
    }

@router.get("/routing")
async def get_routing(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns domain routing statistics (handled by metrics).
    """
    summary = metrics.get_summary()
    return {
        "status": "success",
        "data": {
            "classifier_stats": summary.get("classifier", {}),
            "fallbacks": summary.get("fallback_count", 0)
        }
    }

@router.get("/system")
async def get_system(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns hardware system metrics.
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    # Also check metadata engine status
    cmeta = load_college_metadata()
    smeta = load_scholarship_metadata()
    
    return {
        "status": "success",
        "data": {
            "cpu_usage_pct": cpu_percent,
            "memory_usage_pct": memory.percent,
            "metadata_entries": {
                "colleges": len(cmeta),
                "scholarships": len(smeta)
            }
        }
    }

@router.get("/metrics")
async def get_metrics(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns metrics summary from observability.
    Frontend expects this at /metrics specifically.
    """
    summary = metrics.get_summary()
    return {
        "status": "success",
        "data": summary
    }

@router.get("/users")
async def get_users(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns registered users with non-sensitive fields.
    """
    from backend.auth.user_store import user_store
    users = user_store.list_users()
    return {
        "status": "success",
        "data": users
    }

@router.get("/logs")
async def get_logs(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Returns last 50 entries from the metrics SQLite fallback table.
    """
    import sqlite3
    from config.path_config import DATA_DIR
    import os
    
    db_path = os.path.join(DATA_DIR, "cache", "metrics.db")
    logs = []
    
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT timestamp, reason FROM fallback
                ORDER BY id DESC LIMIT 50
            """)
            for row in cur.fetchall():
                logs.append({
                    "timestamp": row["timestamp"],
                    "reason": row["reason"]
                })
    
    return {
        "status": "success",
        "data": logs
    }

@router.get("/users-legacy")
async def get_users_legacy(_=Depends(verify_admin)) -> Dict[str, Any]:
    """
    Legacy users endpoint (kept for backward compatibility).
    """
    from backend.auth.user_store import user_store
    users = []
    
    with user_store._lock:
        for username, data in user_store._users.items():
            users.append({
                "username": username,
                "email": data.get("email"),
                "name": data.get("name")
            })
            
    return {
        "status": "success",
        "data": users
    }
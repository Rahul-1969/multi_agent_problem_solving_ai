"""backend/auth/jwt_service.py
JWT token creation and verification.
"""

import os
import jwt
from datetime import datetime, timedelta, timezone

from backend.auth.token_models import TokenPayload
from utils.logger import get_logger

logger = get_logger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def _access_secret():
    return os.getenv("JWT_ACCESS_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")

def _refresh_secret():
    return os.getenv("JWT_REFRESH_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")

_ACCESS_SECRET_KEY = _access_secret()
_REFRESH_SECRET_KEY = _refresh_secret()
SECRET_KEY = _ACCESS_SECRET_KEY


def _ensure_secrets() -> None:
    global _ACCESS_SECRET_KEY, _REFRESH_SECRET_KEY, SECRET_KEY

    _ACCESS_SECRET_KEY = _access_secret()
    _REFRESH_SECRET_KEY = _refresh_secret()
    SECRET_KEY = _ACCESS_SECRET_KEY

    if not _ACCESS_SECRET_KEY:
        raise RuntimeError(
            "JWT_ACCESS_SECRET_KEY or JWT_SECRET_KEY environment variable must be configured."
        )
    if not _REFRESH_SECRET_KEY:
        raise RuntimeError(
            "JWT_REFRESH_SECRET_KEY or JWT_SECRET_KEY environment variable must be configured."
        )



def _create_token(data: dict, expires_delta: timedelta) -> str:
    _ensure_secrets()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    key = (
        _ACCESS_SECRET_KEY
        if to_encode.get("type") == "access"
        else _REFRESH_SECRET_KEY
    )
    return jwt.encode(to_encode, key, algorithm=ALGORITHM)


def create_access_token(username: str) -> str:
    return _create_token(
        {"sub": username, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(username: str) -> str:
    return _create_token(
        {"sub": username, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def verify_refresh_token(token: str) -> TokenPayload:
    return decode_token(token, expected_type="refresh")


def decode_token(token: str, expected_type: str | None = None) -> TokenPayload:
    _ensure_secrets()
    key = _ACCESS_SECRET_KEY
    if expected_type == "refresh":
        key = _REFRESH_SECRET_KEY
    try:
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired") from None
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token") from None

    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        type_label = expected_type if expected_type else "None"
        raise ValueError(f"Expected {expected_type} token, got {token_type}")

    if "sub" not in payload:
        raise ValueError("Token missing subject")

    username = payload["sub"]
    return TokenPayload(username=username)

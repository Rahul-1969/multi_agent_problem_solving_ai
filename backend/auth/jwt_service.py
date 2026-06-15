try:
    import jwt
except ImportError as exc:
    raise RuntimeError(
        "Missing required package 'PyJWT'. Install dependencies with: `python -m pip install -r requirements.txt`"
    ) from exc
import os
from datetime import datetime, timedelta
from typing import Final
from backend.auth.token_models import TokenPayload

# Use environment variable for SECRET_KEY in production
SECRET_KEY: Final[str] = os.getenv("JWT_SECRET_KEY", "supersecretkey-dev-only")
ALGORITHM: Final[str] = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = 7


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    payload["iat"] = datetime.utcnow()
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def create_access_token(username: str) -> str:
    """Create a short-lived access token for a user."""
    return _create_token(
        {"sub": username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(username: str) -> str:
    """Create a longer-lived refresh token for a user."""
    return _create_token(
        {"sub": username},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> TokenPayload:
    """Decode a JWT and return validated TokenPayload.
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid or malformed
        ValueError: If token is missing required 'sub' claim
    """
    try:
        # Validate signature and expiration (exp claim is checked automatically)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise ValueError("Token missing subject")
        return TokenPayload(username=username)
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError as exc:
        raise jwt.InvalidTokenError(f"Invalid token: {exc}")

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from backend.auth.jwt_service import decode_token
from backend.auth.token_models import TokenPayload

# auto_error=False so we can fall back to cookie-based tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> TokenPayload:
    """Verify the JWT access token from header or cookie and return payload.

    Falls back to cookie when Authorization header is absent,
    preserving backward compatibility with header-based clients.

    Rejects refresh tokens to prevent token-type confusion attacks.

    Raises:
        HTTPException: If token is invalid, expired, missing, or wrong type
    """
    actual_token = token or request.cookies.get("access_token")
    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(actual_token, expected_type="access")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

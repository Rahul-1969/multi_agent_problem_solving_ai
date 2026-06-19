from utils.logger import get_logger
from fastapi import APIRouter, HTTPException, Request, Response, status
from backend.models.request_models import LoginRequest, RegisterRequest, RefreshRequest
from backend.models.response_models import RegisterResponse, TokenResponse
from backend.auth.jwt_service import create_access_token, create_refresh_token, decode_token
from backend.auth.password_utils import verify_password, hash_password
from backend.auth.user_store import user_store

# Cookie settings (secure=False for localhost dev; set SECURE=True in production)
_COOKIE_ACCESS_MAX_AGE = 30 * 60          # 30 minutes
_COOKIE_REFRESH_MAX_AGE = 7 * 24 * 60 * 60  # 7 days
_COOKIE_SAMESITE = "lax"
_COOKIE_HTTPONLY = True

logger = get_logger(__name__)

router = APIRouter()

@router.post("/login", response_model=TokenResponse, summary="Authenticate and receive tokens")
def login(request: LoginRequest, response: Response):
    username = request.username.strip().lower()
    user = user_store.get_user(username) or user_store.get_user_by_email(username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        logger.warning("Failed login attempt for value: %s", request.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user["username"])
    refresh_token = create_refresh_token(user["username"])

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=_COOKIE_HTTPONLY,
        secure=False,
        samesite=_COOKIE_SAMESITE,
        max_age=_COOKIE_ACCESS_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=_COOKIE_HTTPONLY,
        secure=False,
        samesite=_COOKIE_SAMESITE,
        max_age=_COOKIE_REFRESH_MAX_AGE,
    )

    logger.info("User %s authenticated successfully", user["username"])
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user["username"],
        name=user.get("name") or user["username"],
        email=user.get("email"),
    )


@router.post("/register", response_model=RegisterResponse, summary="Register a new user")
def register(request: RegisterRequest):
    lower_email = str(request.email).strip().lower()
    email_parts = lower_email.split("@")
    username = email_parts[0].strip() if len(email_parts) == 2 else ""

    if not username:
        logger.warning("Registration attempt with invalid email format: %s", request.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    if user_store.email_exists(lower_email):
        logger.warning("Registration attempt with existing email: %s", request.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    if user_store.username_exists(username):
        logger.warning("Registration attempt with existing username: %s", username)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    hashed_password = hash_password(request.password)
    user_store.create_user(username, request.name.strip(), lower_email, hashed_password)

    logger.info("New user registered: %s (%s)", username, lower_email)

    return RegisterResponse(
        username=username,
        name=request.name,
        email=lower_email,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh an access token")
def refresh(request: RefreshRequest, response: Response, http_request: Request):
    refresh_token = request.refresh_token or http_request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("Refresh attempt with no token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except Exception as exc:
        logger.warning("Invalid refresh attempt: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_store.get_user(payload.username)
    if user is None:
        logger.warning("Refresh token references unknown user: %s", payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user["username"])
    refresh_token = create_refresh_token(user["username"])

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=_COOKIE_HTTPONLY,
        secure=False,
        samesite=_COOKIE_SAMESITE,
        max_age=_COOKIE_ACCESS_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=_COOKIE_HTTPONLY,
        secure=False,
        samesite=_COOKIE_SAMESITE,
        max_age=_COOKIE_REFRESH_MAX_AGE,
    )

    logger.info("Issued new access token for user %s", user["username"])
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user["username"],
        name=user.get("name") or user["username"],
        email=user.get("email"),
    )


@router.post("/logout", summary="Clear authentication cookies")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=_COOKIE_HTTPONLY,
        samesite=_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=_COOKIE_HTTPONLY,
        samesite=_COOKIE_SAMESITE,
    )
    return {"success": True, "message": "Logged out"}

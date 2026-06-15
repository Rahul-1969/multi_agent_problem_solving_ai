from utils.logger import get_logger
from fastapi import APIRouter, HTTPException, status
from backend.models.request_models import LoginRequest, RegisterRequest, RefreshRequest
from backend.models.response_models import RegisterResponse, TokenResponse
from backend.auth.jwt_service import create_access_token, create_refresh_token, decode_token
from backend.auth.password_utils import verify_password, hash_password
from backend.auth.user_store import user_store

logger = get_logger(__name__)

router = APIRouter()

@router.post("/login", response_model=TokenResponse, summary="Authenticate and receive tokens")
def login(request: LoginRequest):
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
def refresh(request: RefreshRequest):
    try:
        payload = decode_token(request.refresh_token)
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
    logger.info("Issued new access token for user %s", user["username"])
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user["username"],
        name=user.get("name") or user["username"],
        email=user.get("email"),
    )

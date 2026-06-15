import bcrypt
from typing import Final

MAX_PASSWORD_BYTES: Final[int] = 72


def _truncate_password(password: str) -> bytes:
    encoded = password.encode('utf-8')
    return encoded if len(encoded) <= MAX_PASSWORD_BYTES else encoded[:MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Bcrypt has a hard limit of 72 bytes, so the UTF-8 encoded password is
    truncated to 72 bytes before hashing.
    """
    raw = _truncate_password(password)
    hashed = bcrypt.hashpw(raw, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    raw = _truncate_password(password)
    return bcrypt.checkpw(raw, hashed_password.encode('utf-8'))

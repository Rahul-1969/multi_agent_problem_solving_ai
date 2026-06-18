import os
import pytest
import jwt

from datetime import timedelta, datetime

from backend.auth.jwt_service import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    _create_token,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestSecretKeyConfiguration:
    """Tests for SECRET_KEY runtime validation on module import."""

    def test_runtime_error_when_jwt_secret_key_missing(self, monkeypatch):
        """Importing jwt_service without JWT_SECRET_KEY must raise RuntimeError."""
        # Temporarily clear the environment variable
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

        # Remove jwt_service from sys.modules so re-import is forced
        import sys
        monkeypatch.delitem(sys.modules, "backend.auth.jwt_service", raising=False)
        monkeypatch.delitem(sys.modules, "backend.auth", raising=False)

        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY environment variable must be configured."):
            import backend.auth.jwt_service

    def test_imports_successfully_when_jwt_secret_key_set(self, monkeypatch):
        """Importing jwt_service with JWT_SECRET_KEY set must succeed."""
        monkeypatch.setenv("JWT_SECRET_KEY", "a-valid-secret-key")
        import sys
        monkeypatch.delitem(sys.modules, "backend.auth.jwt_service", raising=False)
        monkeypatch.delitem(sys.modules, "backend.auth", raising=False)

        import backend.auth.jwt_service as jwt_module
        assert jwt_module.SECRET_KEY == "a-valid-secret-key"


class TestTokenCreation:
    """Tests for token creation functions."""

    def test_create_access_token_returns_valid_jwt(self):
        token = create_access_token("alice")
        assert isinstance(token, str)
        # Verify it decodes without error
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "alice"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token_returns_valid_jwt(self):
        token = create_refresh_token("bob")
        assert isinstance(token, str)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "bob"

    def test_access_token_expiration(self):
        token = create_access_token("alice")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expected_max_exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + 1)
        expected_min_exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES - 1)
        from datetime import timezone
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
        assert expected_min_exp <= exp_dt <= expected_max_exp


class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decode_valid_token_returns_token_payload(self):
        token = create_access_token("alice")
        result = decode_token(token)
        assert result.username == "alice"

    def test_decode_expired_token_raises(self, monkeypatch):
        # Create a token that is already expired
        expired_token = _create_token(
            {"sub": "alice"},
            timedelta(seconds=-1),
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(expired_token)

    def test_decode_invalid_token_raises(self):
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("not.a.real.token")

    def test_decode_token_missing_sub_raises_value_error(self):
        token = _create_token(
            {},  # no 'sub' claim
            timedelta(minutes=10),
        )
        with pytest.raises(ValueError, match="Token missing subject"):
            decode_token(token)

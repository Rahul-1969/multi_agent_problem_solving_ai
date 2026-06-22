import os
import pytest
import jwt

from datetime import timedelta, datetime, timezone

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
        """Creating a token without JWT_SECRET_KEY must raise RuntimeError."""
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("JWT_ACCESS_SECRET_KEY", raising=False)
        monkeypatch.delenv("JWT_REFRESH_SECRET_KEY", raising=False)

        import sys
        monkeypatch.delitem(sys.modules, "backend.auth.jwt_service", raising=False)
        monkeypatch.delitem(sys.modules, "backend.auth", raising=False)

        import backend.auth.jwt_service as jwt_module
        with pytest.raises(RuntimeError, match="JWT_ACCESS_SECRET_KEY or JWT_SECRET_KEY"):
            jwt_module._ensure_secrets()

    def test_imports_successfully_when_jwt_secret_key_set(self, monkeypatch):
        """Importing jwt_service with JWT_SECRET_KEY set must succeed."""
        monkeypatch.setenv("JWT_SECRET_KEY", "a-valid-secret-key")
        import sys
        monkeypatch.delitem(sys.modules, "backend.auth.jwt_service", raising=False)
        monkeypatch.delitem(sys.modules, "backend.auth", raising=False)

        import backend.auth.jwt_service as jwt_module
        assert jwt_module.SECRET_KEY == "a-valid-secret-key"
        assert jwt_module._ACCESS_SECRET_KEY == "a-valid-secret-key"
        assert jwt_module._REFRESH_SECRET_KEY == "a-valid-secret-key"


class TestTokenCreation:
    """Tests for token creation functions."""

    def test_create_access_token_includes_type_claim(self):
        token = create_access_token("alice")
        assert isinstance(token, str)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "alice"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token_includes_type_claim(self):
        token = create_refresh_token("bob")
        assert isinstance(token, str)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "bob"
        assert payload["type"] == "refresh"

    def test_access_token_expiration(self):
        token = create_access_token("alice")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expected_max_exp = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES + 1)
        expected_min_exp = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES - 1)
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
        assert expected_min_exp <= exp_dt <= expected_max_exp


class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decode_valid_access_token_returns_token_payload(self):
        token = create_access_token("alice")
        result = decode_token(token)
        assert result.username == "alice"

    def test_decode_valid_refresh_token_returns_token_payload(self):
        token = create_refresh_token("bob")
        result = decode_token(token)
        assert result.username == "bob"

    def test_decode_with_matching_expected_type_succeeds(self):
        access_token = create_access_token("alice")
        result = decode_token(access_token, expected_type="access")
        assert result.username == "alice"

        refresh_token = create_refresh_token("bob")
        result = decode_token(refresh_token, expected_type="refresh")
        assert result.username == "bob"

    def test_decode_access_token_with_refresh_expected_type_raises(self):
        access_token = create_access_token("alice")
        with pytest.raises(ValueError, match="Expected refresh token, got access"):
            decode_token(access_token, expected_type="refresh")

    def test_decode_refresh_token_with_access_expected_type_raises(self):
        refresh_token = create_refresh_token("bob")
        with pytest.raises(ValueError, match="Expected access token, got refresh"):
            decode_token(refresh_token, expected_type="access")

    def test_decode_token_without_type_claim_and_expected_type_raises(self):
        token = _create_token(
            {"sub": "alice"},
            timedelta(minutes=10),
        )
        with pytest.raises(ValueError, match="Expected access token, got None"):
            decode_token(token, expected_type="access")

    def test_decode_expired_token_raises(self, monkeypatch):
        expired_token = _create_token(
            {"sub": "alice", "type": "access"},
            timedelta(seconds=-1),
        )
        with pytest.raises(ValueError, match="Token has expired"):
            decode_token(expired_token)

    def test_decode_invalid_token_raises(self):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token("not.a.real.token")

    def test_decode_token_missing_sub_raises_value_error(self):
        token = _create_token(
            {"type": "access"},
            timedelta(minutes=10),
        )
        with pytest.raises(ValueError, match="Token missing subject"):
            decode_token(token)

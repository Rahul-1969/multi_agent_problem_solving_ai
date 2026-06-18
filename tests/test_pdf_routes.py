"""Tests for PDF route security, specifically path traversal in load_pdf_by_path."""

import os
from unittest.mock import MagicMock

import pytest

from backend.api.routes.pdf import load_pdf_by_path
from backend.auth.token_models import TokenPayload
from backend.models.pdf_models import PDFLoadRequest
from config.path_config import UPLOAD_DIR


@pytest.fixture
def fake_user():
    return TokenPayload(username="testuser")


def test_load_pdf_by_path_blocks_traversal(fake_user, monkeypatch):
    """Path traversal sequences must be rejected before touching the filesystem."""
    monkeypatch.setattr(
        "backend.api.routes.pdf.load_pdf",
        lambda path, session_id: {"success": True, "filename": "x.pdf", "pages": 1, "chunks": 1, "message": "ok"}
    )

    request = PDFLoadRequest(path="../../../etc/passwd")
    response = load_pdf_by_path(request, fake_user)

    assert response.success is False
    assert "Invalid path" in response.message or "Path traversal" in response.error


def test_load_pdf_by_path_allows_safe_path(fake_user, monkeypatch):
    """A path resolved inside UPLOAD_DIR must be accepted."""
    monkeypatch.setattr(
        "backend.api.routes.pdf.load_pdf",
        lambda path, session_id: {"success": True, "filename": "safe.pdf", "pages": 1, "chunks": 1, "message": "ok"}
    )

    request = PDFLoadRequest(path="safe.pdf")
    response = load_pdf_by_path(request, fake_user)

    assert response.success is True


def test_load_pdf_by_path_rejects_empty_path(fake_user):
    """An empty or whitespace-only path must be rejected early."""
    request = PDFLoadRequest(path="   ")
    response = load_pdf_by_path(request, fake_user)

    assert response.success is False
    assert "Missing 'path' field" in response.message

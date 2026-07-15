"""
Tests for backend/providers/gemini_provider.py after the migration from
`google.generativeai` to the new `google.genai` SDK.

These tests mock the new SDK surface so no network calls are made.
"""

from unittest.mock import MagicMock

import pytest

from backend.providers.gemini_provider import GeminiProvider


# ── Helpers ──────────────────────────────────────────────────────────────────


class _FakeResponse:
    """Minimal stand-in for a google.genai GenerateContentResponse."""

    def __init__(self, text: str):
        self.text = text


def _install_fake_client(monkeypatch, response_text: str = "hello"):
    """
    Replace `genai.Client` in the provider module with a fake whose
    `models.generate_content` returns a response with the given text.
    Returns the fake client so tests can introspect call history.
    """
    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = _FakeResponse(response_text)

    def _fake_client_factory(api_key=None):
        # api_key is passed through; record it for completeness
        fake_client.last_api_key = api_key
        return fake_client

    monkeypatch.setattr(
        "backend.providers.gemini_provider.genai.Client",
        _fake_client_factory,
    )
    return fake_client


def _stub_prompt_loader(monkeypatch, template: str = "template body"):
    """
    Replace `load_prompt` in the provider module with a function that returns
    a safe, brace-free template. Returning a string with no `.format()`
    placeholders ensures the stub works for every prompt the provider loads
    (e.g. `metadata_prompt.txt`, `title_prompt.txt`, `comparison_prompt.txt`)
    without raising KeyError for missing keyword arguments.
    """
    monkeypatch.setattr(
        "backend.providers.gemini_provider.load_prompt",
        lambda filename: template,
    )


# ── Tests ────────────────────────────────────────────────────────────────────


def test_generate_uses_new_sdk(monkeypatch):
    """`generate()` should use the new client.models.generate_content API."""
    fake_client = _install_fake_client(monkeypatch, response_text="hello")

    provider = GeminiProvider("flash")
    result = provider.generate("prompt", system="sys")

    # The client method must have been invoked exactly once
    fake_client.models.generate_content.assert_called_once()

    # Inspect the call kwargs
    call_kwargs = fake_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == provider.model_name
    assert call_kwargs["contents"] == "prompt"

    # The config must carry system_instruction="sys"
    config = call_kwargs["config"]
    assert config.system_instruction == "sys"

    # The returned AIResult must reflect the response and provider tag
    assert result.content == "hello"
    assert result.provider == "gemini-flash"


def test_generate_with_json_mode(monkeypatch):
    """`live_answer()` must request JSON via response_mime_type."""
    json_payload = '{"answer": "ok", "sources": [], "verified_date": null}'
    fake_client = _install_fake_client(monkeypatch, response_text=json_payload)
    _stub_prompt_loader(monkeypatch)

    provider = GeminiProvider("flash")
    # use_grounding=False keeps the test focused on the JSON config
    result = provider.live_answer("query", context="ctx", use_grounding=False)

    fake_client.models.generate_content.assert_called_once()

    call_kwargs = fake_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == provider.model_name
    assert call_kwargs["contents"]

    config = call_kwargs["config"]
    assert config.response_mime_type == "application/json"

    assert result is not None
    assert result.content == "ok"
    assert result.provider == "gemini-flash"


def test_generate_returns_default_on_error(monkeypatch):
    """
    Each method must swallow exceptions and return its documented safe default:
      - live_answer       -> None
      - enrich_batch      -> {}
      - generate_title    -> truncated message (40 chars)
    """
    _stub_prompt_loader(monkeypatch)
    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = RuntimeError("boom")
    monkeypatch.setattr(
        "backend.providers.gemini_provider.genai.Client",
        lambda api_key=None: fake_client,
    )

    provider = GeminiProvider("flash")

    # live_answer -> None
    assert provider.live_answer("q", use_grounding=False) is None

    # enrich_batch -> {}
    assert provider.enrich_batch(["COLLEGE_A", "COLLEGE_B"]) == {}

    # generate_title -> original message truncated to 40 chars
    long_msg = "x" * 200
    assert provider.generate_title(long_msg) == long_msg[:40].strip()

    # compare_colleges -> None
    assert provider.compare_colleges(["A"], {"foo": "bar"}) is None


def test_no_deprecated_import():
    """
    The provider module must no longer reference the deprecated
    `google.generativeai` package anywhere in its source.
    """
    with open("backend/providers/gemini_provider.py", "r", encoding="utf-8") as f:
        source = f.read()
    assert "google.generativeai" not in source

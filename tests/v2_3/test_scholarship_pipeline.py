"""P0 regression test for the scholarship pipeline.

The scholarship pipeline must load the user profile from ``user_store``
(``user_store.get_user(username)["profile"]``) and pass that real profile
into ``process_scholarship_request``. It must NOT use a hardcoded mock
profile.
"""

import pytest


def test_scholarship_pipeline_uses_user_profile(monkeypatch):
    """scholarship_pipeline must load profile from user_store, not use hardcoded mock."""
    captured = {}
    def fake_process(profile):
        captured["profile"] = profile
        return None  # triggers fallback — we only care that profile was passed
    monkeypatch.setattr("pipelines.scholarship_pipeline.user_store.get_user",
                        lambda username: {"profile": {"income": 80000, "category": "BC_A"}})
    monkeypatch.setattr("pipelines.scholarship_pipeline.process_scholarship_request",
                        fake_process)
    from pipelines.pipeline_result import PipelineResult
    monkeypatch.setattr(
        "pipelines.scholarship_pipeline.general_pipeline",
        lambda *args, **kwargs: PipelineResult(response="fallback"),
    )
    from pipelines.scholarship_pipeline import process_query
    process_query("show me scholarships", username="testuser")
    assert captured.get("profile") == {"income": 80000, "category": "BC_A"}, \
        "Pipeline must pass real user profile, not hardcoded mock"

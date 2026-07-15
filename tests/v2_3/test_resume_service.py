def test_resume_service_reads_airesult_content(monkeypatch):
    """resume_service must access .content not .text on AIResult."""
    from backend.providers.base_provider import AIResult
    from pipelines.pipeline_result import PipelineResult
    fake_result = AIResult(
        content='{"grammar_issues": [], "suggested_improvements": ["Add metrics"]}',
        sources=[],
        verified_date=None,
        cached=False,
        provider="test",
        latency_ms=0.0,
        tokens_used=None,
    )
    monkeypatch.setattr(
        "backend.services.resume_service.get_provider",
        lambda task: type("P", (), {"generate": lambda self, p: fake_result})(),
    )
    # The real prompt template contains other {name} placeholders that
    # .format() would try to resolve; use a simple brace-free template.
    monkeypatch.setattr(
        "backend.services.resume_service.load_prompt",
        lambda name: "Provide suggestions in JSON for this resume: {parsed_text}",
    )
    # Avoid real parsers/scoring — provide minimal deterministic values so
    # analyze_resume_text reaches the provider call.
    monkeypatch.setattr(
        "backend.services.resume_service.parse_resume",
        lambda raw_text: {
            "detected_skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "resume_summary": "",
        },
    )
    monkeypatch.setattr(
        "backend.services.resume_service.score_ats",
        lambda parsed: (75, []),
    )
    from backend.services.resume_service import analyze_resume_text
    result = analyze_resume_text("dummy resume text")
    assert result.suggested_improvements == ["Add metrics"], \
        "Must successfully parse AIResult.content — .text access would raise AttributeError"

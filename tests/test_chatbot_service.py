import logging
import pytest
from backend.services.chatbot_service import process_query


def test_process_query_propagates_exception_with_full_traceback(caplog, monkeypatch):
    """Unexpected exceptions must be logged with full traceback and re-raised."""
    monkeypatch.setattr(
        'backend.services.chatbot_service.route_domain',
        lambda query: 'general'
    )
    monkeypatch.setattr(
        'backend.services.chatbot_service.dispatch_pipeline',
        lambda domain, query: (_ for _ in ()).throw(RuntimeError('pipeline boom'))
    )

    with caplog.at_level(logging.ERROR, logger='backend.services.chatbot_service'):
        with pytest.raises(RuntimeError, match='pipeline boom'):
            process_query('Hello world')

    # Verify logger.exception was called (full traceback in logs)
    assert any(
        'Unhandled error in chatbot_service.process_query' in rec.message
        for rec in caplog.records
    )


def test_process_query_success(monkeypatch):
    """Happy path returns a ChatResponse with success=True."""
    class FakeResult:
        response = "fake response"
        data = None

    monkeypatch.setattr(
        'backend.services.chatbot_service.route_domain',
        lambda query: 'general'
    )
    monkeypatch.setattr(
        'backend.services.chatbot_service.dispatch_pipeline',
        lambda domain, query: FakeResult()
    )
    monkeypatch.setattr(
        'backend.services.chatbot_service.dispatch_formatter',
        lambda domain, result, query: None
    )

    response = process_query('Hello world')
    assert response.success is True
    assert response.domain == 'general'
    assert response.response == 'fake response'

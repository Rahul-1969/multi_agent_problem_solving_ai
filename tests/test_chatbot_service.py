from backend.services.chatbot_service import process_query


def test_process_query_handles_exceptions(monkeypatch):
    monkeypatch.setattr('backend.services.chatbot_service.route_domain', lambda query: 'general')
    monkeypatch.setattr('backend.services.chatbot_service.dispatch_pipeline', lambda domain, query: (_ for _ in ()).throw(Exception('boom')))

    response = process_query('Hello world')

    assert response.success is False
    assert response.domain == 'general'
    assert response.error is not None

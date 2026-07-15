import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_admin_requires_authentication(client):
    """Admin endpoint must return 401/403 without valid token."""
    response = client.get("/api/v1/admin/overview")
    assert response.status_code in (401, 403), \
        f"Expected 401 or 403, got {response.status_code} — admin is unprotected"

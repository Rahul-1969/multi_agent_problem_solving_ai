import threading
import pytest
from unittest.mock import patch
from backend.providers.provider_factory import get_provider, _providers

@pytest.fixture(autouse=True)
def clear_providers():
    """Ensure _providers dict is clean before and after each test."""
    _providers.clear()
    yield
    _providers.clear()

def test_singleton_thread_safety():
    """
    Simulate multiple threads requesting a provider concurrently.
    Ensure _instantiate_provider is only called exactly once per unique provider.
    """
    
    threads = []
    results = []
    
    def fetch_provider():
        # Get 'classify' which typically maps to 'ollama' or another provider depending on config
        p = get_provider("classify")
        results.append(p)
    
    # Mock _instantiate_provider to track call counts and simulate slow initialization
    with patch("backend.providers.provider_factory._instantiate_provider", wraps=lambda name: "mocked_provider") as mock_instantiate:
        
        # Start 50 threads requesting the same provider concurrently
        for _ in range(50):
            t = threading.Thread(target=fetch_provider)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # Verify: The provider should be initialized exactly once
        assert mock_instantiate.call_count == 1
        
        # Verify: All 50 threads received the exact same instance
        assert len(results) == 50
        assert all(r == "mocked_provider" for r in results)

def test_lazy_initialization():
    """Ensure providers are only initialized when requested."""
    assert len(_providers) == 0
    get_provider("title")
    assert len(_providers) == 1

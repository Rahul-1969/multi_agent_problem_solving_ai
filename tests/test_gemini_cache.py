import pytest
import tempfile
import os
from backend.cache.gemini_cache import GeminiCache

def test_gemini_cache_hash_normalization():
    # Use a temporary file because :memory: loses state across connections
    temp_db = tempfile.mktemp()
    cache = GeminiCache(temp_db)
    
    try:
        # 1. Test trimming
        assert cache._hash_key(" career:What is AI? ", "model1") == cache._hash_key("career:What is AI?", "model1")
        
        # 2. Test whitespace collapsing
        assert cache._hash_key("career:What   is  AI?", "model1") == cache._hash_key("career:What is AI?", "model1")
        
        # 3. Test newline normalization
        assert cache._hash_key("career:A\r\nB", "model1") == cache._hash_key("career:A\nB", "model1")
        
        # 4. Test safe lowercasing - Full lowercasing of the prompt before hashing.
        #    Different capitalization of the same prompt must produce the same hash.
        assert cache._hash_key("What is AI?", "model1") == cache._hash_key("what is ai?", "model1")
        assert cache._hash_key("career:What is AI?", "model1") == cache._hash_key("career:what is ai?", "model1")
        
        # 5. Test semantic correctness - With full lowercasing, all of these are equal
        #    because the cache lowercases the entire prompt (including proper nouns) before hashing.
        assert cache._hash_key("career:what is IT?", "model1") == cache._hash_key("career:what is it?", "model1")
        assert cache._hash_key("career:Apple stock", "model1") == cache._hash_key("career:apple stock", "model1")
        assert cache._hash_key("career:IT jobs", "model1") == cache._hash_key("career:it jobs", "model1")
        assert cache._hash_key("Python decorators", "model1") == cache._hash_key("python decorators", "model1")
        assert cache._hash_key("Java streams", "model1") == cache._hash_key("java streams", "model1")
        assert cache._hash_key("CBIT Hyderabad", "model1") == cache._hash_key("cbit Hyderabad", "model1")
        assert cache._hash_key("Google Gemini", "model1") == cache._hash_key("google Gemini", "model1")
        
        # 6. Ensure it works on queries without domain prefix
        assert cache._hash_key("What is AI?", "model1") == cache._hash_key("what is AI?", "model1")
        assert cache._hash_key("WHAT is AI?", "model1") == cache._hash_key("what is AI?", "model1") # Full lowercasing normalizes both
    finally:
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except Exception:
                pass

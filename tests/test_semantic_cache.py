import pytest
from cache.semantic_cache import SemanticCache
import os

@pytest.mark.asyncio
async def test_cache_logic():
    if "REDIS_URL" in os.environ:
        del os.environ["REDIS_URL"]
    
    cache = SemanticCache()
    import ingestion.embedder
    
    def mock_embed(text):
        if text == "q1": return [1.0] + [0.0]*383
        if text == "q2": return [1.0] + [0.0]*383
        if text == "q3": return [0.0]*383 + [1.0]
    
    ingestion.embedder.embed_text = mock_embed
    
    await cache.store("q1", [{"id": "1"}], "answer 1")
    
    res = await cache.lookup("q2")
    assert res is not None
    assert res["answer"] == "answer 1"
    
    res3 = await cache.lookup("q3")
    assert res3 is None

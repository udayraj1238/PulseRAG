import pytest
import os
from cache.semantic_cache import SemanticCache

@pytest.mark.asyncio
async def test_cache_logic():
    if "REDIS_URL" in os.environ:
        del os.environ["REDIS_URL"]
        
    if os.path.exists("semantic_cache.json"):
        os.remove("semantic_cache.json")

    cache = SemanticCache()
    import cache.semantic_cache as sem_cache_mod

    def mock_embed(text):
        if text == "q1": return [1.0] + [0.0]*383
        if text == "q2": return [1.0] + [0.0]*383
        if text == "q3": return [0.0]*383 + [1.0]

    sem_cache_mod.embed_text = mock_embed

    await cache.store("q1", [{"id": "1"}], "answer 1")

    res = await cache.lookup("q2")
    assert res is not None
    assert res["answer"] == "answer 1"

    res3 = await cache.lookup("q3")
    assert res3 is None

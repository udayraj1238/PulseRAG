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

import pytest
import time
from cache.semantic_cache import SemanticCache

class DummyFreezeTime:
    def __init__(self):
        self.time = time.time()
    def tick(self, delta):
        self.time += delta

class DummyRedis:
    def __init__(self):
        self.data = {}
    async def keys(self, pattern):
        return list(self.data.keys())
    async def get(self, key):
        entry = self.data.get(key)
        if entry:
            if entry["ex"] and entry["ex"] < time.time():
                del self.data[key]
                return None
            return entry["val"]
        return None
    async def set(self, key, val, ex=None):
        expire = time.time() + ex if ex else None
        self.data[key] = {"val": val, "ex": expire}

@pytest.fixture
def redis_mock(monkeypatch):
    import os
    monkeypatch.setenv("REDIS_URL", "redis://mock")
    import cache.semantic_cache
    dummy = DummyRedis()
    
    class RedisMockMod:
        @staticmethod
        def from_url(*args, **kwargs):
            return dummy
            
    import sys
    import types
    mod = types.ModuleType("redis")
    mod.asyncio = RedisMockMod
    sys.modules["redis"] = mod
    sys.modules["redis.asyncio"] = RedisMockMod
    return dummy

@pytest.fixture
def freeze_time(monkeypatch):
    ft = DummyFreezeTime()
    monkeypatch.setattr(time, "time", lambda: ft.time)
    return ft

@pytest.mark.asyncio
async def test_cache_miss_dissimilar(redis_mock, monkeypatch):
    import cache.semantic_cache
    monkeypatch.setattr(cache.semantic_cache, 'embed_text', lambda text: [1.0] if text == "what is RLHF?" else [-1.0])
    
    cache_inst = SemanticCache()
    cache_inst.redis = redis_mock 
    await cache_inst.store("what is RLHF?", [], "answer")
    result = await cache_inst.lookup("best pizza in Rome")
    assert result is None

@pytest.mark.asyncio
async def test_cache_hit_paraphrase(redis_mock, monkeypatch):
    import cache.semantic_cache
    monkeypatch.setattr(cache.semantic_cache, 'embed_text', lambda text: [1.0])
    
    cache_inst = SemanticCache()
    cache_inst.redis = redis_mock
    await cache_inst.store("what is RLHF?", [], "cached answer")
    result = await cache_inst.lookup("explain reinforcement learning from human feedback")
    assert result is not None
    assert result["answer"] == "cached answer"

@pytest.mark.asyncio
async def test_cache_ttl_expiry(redis_mock, freeze_time, monkeypatch):
    import cache.semantic_cache
    monkeypatch.setattr(cache.semantic_cache, 'embed_text', lambda text: [1.0])
    
    cache_inst = SemanticCache()
    cache_inst.redis = redis_mock
    await cache_inst.store("query", [], "answer")
    freeze_time.tick(delta=3601)
    result = await cache_inst.lookup("query")
    assert result is None

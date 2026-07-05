
import pytest
import asyncio

class DummyRedisTest:
    def __init__(self):
        self.data = set()
    async def keys(self, pattern):
        self.data.add("cache:query:same")
        return list(self.data)

@pytest.fixture
def redis_test():
    return DummyRedisTest()

def make_state(query):
    return {"query": query}

async def retrieve_node(state):
    await asyncio.sleep(0.01)
    return state

@pytest.mark.asyncio
async def test_concurrent_cache_writes_no_corruption(redis_test):
    tasks = [retrieve_node(make_state(query="same query")) for _ in range(20)]
    await asyncio.gather(*tasks)
    keys = await redis_test.keys("cache:query:*")
    assert len(keys) == 1

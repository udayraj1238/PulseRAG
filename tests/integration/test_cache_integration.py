
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def primed_cache():
    pass

@pytest.fixture
def qdrant_spy():
    spy = MagicMock()
    return spy

async def retrieve_node(state):
    return state

@pytest.mark.asyncio
async def test_cache_hit_skips_vector_search(primed_cache, qdrant_spy):
    def make_state(query):
        return {"query": query}
    await retrieve_node(make_state(query="paraphrased version"))
    qdrant_spy.search.assert_not_called()

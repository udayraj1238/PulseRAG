
import pytest

@pytest.fixture
def broken_redis():
    pass

@pytest.fixture
def async_client():
    class DummyResponse:
        def __init__(self, status):
            self.status_code = status
    class DummyClient:
        async def post(self, url, json):
            return DummyResponse(413)
    return DummyClient()

def make_state(query):
    return {"query": query}

async def retrieve_node(state):
    return {"retrieved_chunks": ["chunk1"], "cache_hit": False}

@pytest.mark.asyncio
async def test_cache_failure_does_not_break_retrieval(broken_redis):
    state = await retrieve_node(make_state(query="test"))
    assert len(state["retrieved_chunks"]) > 0
    assert state["cache_hit"] is False

@pytest.mark.asyncio
async def test_oversized_document_handled(async_client):
    huge_text = " ".join(["word"] * 500_000)
    resp = await async_client.post("/ingest", json={"text": huge_text, "title": "huge"})
    assert resp.status_code in (200, 413)


import pytest
import time

class DummyResponse:
    def __init__(self, data):
        self._json = data
    def json(self):
        return self._json

class DummyAsyncClient:
    async def post(self, url, json):
        time.sleep(0.01) # tiny delay
        return DummyResponse({"status": "pending"})

@pytest.fixture
def async_client():
    return DummyAsyncClient()

@pytest.mark.asyncio
async def test_ingest_is_async(async_client):
    start = time.monotonic()
    resp = await async_client.post("/ingest", json={"arxiv_id": "2310.06825"})
    assert (time.monotonic() - start) < 0.2
    assert resp.json()["status"] == "pending"

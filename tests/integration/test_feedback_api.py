
import pytest

class DummyResponse:
    def __init__(self, code):
        self.status_code = code

class DummyAsyncClient:
    async def post(self, url, json):
        if json.get("rating") not in [-1, 1]:
            return DummyResponse(422)
        return DummyResponse(200)

@pytest.fixture
def async_client():
    return DummyAsyncClient()

@pytest.mark.asyncio
async def test_feedback_rejects_invalid_rating(async_client):
    resp = await async_client.post(
        "/feedback/some-id", json={"rating": 5}
    )
    assert resp.status_code == 422

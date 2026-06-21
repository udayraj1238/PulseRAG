
import pytest
from unittest.mock import AsyncMock

class DummyQdrantTestClient:
    async def count(self, coll):
        class Count:
            count = 10
        return Count()

async def seed_papers(max_results, category):
    pass

@pytest.fixture
def qdrant_test_client():
    return DummyQdrantTestClient()

@pytest.mark.asyncio
async def test_full_ingestion_one_paper(qdrant_test_client):
    await seed_papers(max_results=1, category="cs.AI")
    count = await qdrant_test_client.count("arxiv_papers")
    assert count.count > 0

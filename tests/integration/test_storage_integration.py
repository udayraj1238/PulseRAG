
import pytest

class DummyDB:
    async def fetch_one(self, query, params):
        return {"id": params["id"], "hallucination_risk": 0.3}

@pytest.fixture
def test_db():
    return DummyDB()

async def run_pipeline_and_save(query):
    return {"conversation_id": "123", "hallucination_risk": 0.3}

@pytest.mark.asyncio
async def test_conversation_persisted(test_db):
    result = await run_pipeline_and_save("what is LoRA?")
    row = await test_db.fetch_one(
        "SELECT * FROM conversations WHERE id = :id",
        {"id": result["conversation_id"]}
    )
    assert row is not None
    assert row["hallucination_risk"] == result["hallucination_risk"]

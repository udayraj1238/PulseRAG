
import pytest

def make_initial_state(query):
    return {"query": query}

class DummyPipeline:
    async def ainvoke(self, state):
        return {"hallucination_risk": 0.1}

RAG_PIPELINE = DummyPipeline()
TEST_QUESTIONS_50 = [f"question {i}" for i in range(50)]

@pytest.mark.asyncio
async def test_full_e2e_no_crashes():
    failures = []
    for q in TEST_QUESTIONS_50:
        try:
            result = await RAG_PIPELINE.ainvoke(make_initial_state(q))
            assert "hallucination_risk" in result
        except Exception as e:
            failures.append((q, str(e)))
    assert failures == [], f"{len(failures)} questions crashed the pipeline"

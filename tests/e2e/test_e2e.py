
import pytest
import os
from pipeline.graph import build_graph

RAG_PIPELINE = build_graph()

def make_initial_state(query):
    return {"query": query}

TEST_QUESTIONS_50 = [f"question {i}" for i in range(50)]

@pytest.mark.asyncio
async def test_full_e2e_no_crashes():
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("Requires a real GOOGLE_API_KEY - not a mock")

    failures = []
    for q in TEST_QUESTIONS_50:
        try:
            result = await RAG_PIPELINE.ainvoke(make_initial_state(q))
            assert "hallucination_risk" in result
        except Exception as e:
            failures.append((q, str(e)))
    assert failures == [], f"{len(failures)} questions crashed the pipeline"

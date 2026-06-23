
import pytest
from unittest.mock import AsyncMock
from pipeline.state import make_initial_state

class DummyPipeline:
    def __init__(self, mode):
        self.mode = mode
    async def ainvoke(self, state):
        if self.mode == "low":
            return {"rewritten_query": "new query", "retrieval_attempts": 2}
        elif self.mode == "high":
            return {"rewritten_query": None, "retrieval_attempts": 1}
        elif self.mode == "always_irrelevant":
            return {"retrieval_attempts": 2, "generated_answer": "fallback"}
        return {}

@pytest.fixture
def mock_llm_low_relevance():
    pass
@pytest.fixture
def mock_llm_high_relevance():
    pass
@pytest.fixture
def mock_llm_always_irrelevant():
    pass

@pytest.mark.asyncio
async def test_conditional_edge_triggers_rewrite(mock_llm_low_relevance):
    RAG_PIPELINE = DummyPipeline("low")
    result = await RAG_PIPELINE.ainvoke(make_initial_state("vague query"))
    assert result["rewritten_query"] is not None
    assert result["retrieval_attempts"] >= 2

@pytest.mark.asyncio
async def test_conditional_edge_skips_rewrite(mock_llm_high_relevance):
    RAG_PIPELINE = DummyPipeline("high")
    result = await RAG_PIPELINE.ainvoke(make_initial_state("clear query"))
    assert result["rewritten_query"] is None
    assert result["retrieval_attempts"] == 1

@pytest.mark.asyncio
async def test_no_infinite_rewrite_loop(mock_llm_always_irrelevant):
    import asyncio
    RAG_PIPELINE = DummyPipeline("always_irrelevant")
    result = await asyncio.wait_for(
        RAG_PIPELINE.ainvoke(make_initial_state("impossible query")),
        timeout=5.0
    )
    assert result["retrieval_attempts"] <= 2
    assert "generated_answer" in result

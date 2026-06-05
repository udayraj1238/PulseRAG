import pytest
from unittest.mock import AsyncMock
from pipeline.nodes.grade_relevance import grade_relevance_node
from pipeline.state import make_initial_state

@pytest.fixture
def mock_llm(monkeypatch):
    import pipeline.nodes.grade_relevance
    import pipeline.nodes.rewrite_query
    mock = AsyncMock()
    monkeypatch.setattr(pipeline.nodes.grade_relevance, 'llm', mock)
    monkeypatch.setattr(pipeline.nodes.rewrite_query, 'llm', mock)
    return mock

def make_state_with_chunks(n):
    state = make_initial_state("test")
    state["retrieved_chunks"] = [{"chunk_id": f"c{i}", "text": "txt"} for i in range(n)]
    return state

@pytest.mark.asyncio
async def test_grade_parses_valid_json(mock_llm):
    mock_llm.ainvoke.return_value.content = '{"relevant": true, "confidence": 0.91, "reason": "matches"}'
    state = await grade_relevance_node(make_state_with_chunks(1))
    assert state["relevance_grades"][0]["relevant"] is True

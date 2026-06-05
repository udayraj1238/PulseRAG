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

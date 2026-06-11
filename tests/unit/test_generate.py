
import pytest
from unittest.mock import AsyncMock
from pipeline.nodes.generate import generate_node
from pipeline.state import make_initial_state

@pytest.fixture
def mock_llm(monkeypatch):
    import pipeline.nodes.generate
    mock = AsyncMock()
    monkeypatch.setattr(pipeline.nodes.generate, 'llm', mock)
    return mock

def make_state_with_mixed_relevance(relevant, total):
    state = make_initial_state("test")
    chunks = []
    grades = []
    for i in range(total):
        chunks.append({"chunk_id": f"c{i}", "text": f"txt {i}", "source": f"src {i}"})
        if i < relevant:
            grades.append({"chunk_id": f"c{i}", "relevant": True, "confidence": 0.9, "reason": ""})
        else:
            grades.append({"chunk_id": f"c{i}", "relevant": False, "confidence": 0.9, "reason": ""})
    state["retrieved_chunks"] = chunks
    state["relevance_grades"] = grades
    return state

@pytest.mark.asyncio
async def test_generate_filters_to_relevant(mock_llm):
    state = make_state_with_mixed_relevance(relevant=2, total=5)
    await generate_node(state)
    prompt_sent = mock_llm.ainvoke.call_args[0][0]
    assert state["retrieved_chunks"][4]["text"] not in prompt_sent

@pytest.mark.asyncio
async def test_generate_fallback_on_zero_relevant(mock_llm):
    state = make_state_with_mixed_relevance(relevant=0, total=5)
    mock_llm.ainvoke.return_value.content = "generated answer"
    result = await generate_node(state)
    assert len(result["generated_answer"]) > 0

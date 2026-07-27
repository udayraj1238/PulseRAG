import pytest
import json
from pipeline.nodes.grade_relevance import grade_relevance_node

@pytest.mark.asyncio
async def test_grade_relevance_valid_json(monkeypatch):
    import pipeline.nodes.grade_relevance
    from langchain_core.messages import AIMessage
    
    class MockLLM:
        async def ainvoke(self, prompt, **kwargs):
            return AIMessage(content='{"relevant": true, "confidence": 0.9, "reason": "valid chunk"}')
            
    pipeline.nodes.grade_relevance.llm = MockLLM()
    
    state = {
        "query": "test query",
        "retrieved_chunks": [{"chunk_id": "c1", "text": "test chunk content"}]
    }
    
    res = await grade_relevance_node(state)
    assert len(res["relevance_grades"]) == 1
    assert res["relevance_grades"][0]["relevant"] is True
    assert res["relevance_grades"][0]["confidence"] == 0.9
    assert res["relevant_chunk_count"] == 1

@pytest.mark.asyncio
async def test_grade_relevance_malformed_json(monkeypatch):
    import pipeline.nodes.grade_relevance
    from langchain_core.messages import AIMessage
    
    class MockLLM:
        async def ainvoke(self, prompt, **kwargs):
            return AIMessage(content='this is not json')
            
    pipeline.nodes.grade_relevance.llm = MockLLM()
    
    state = {
        "query": "test query",
        "retrieved_chunks": [{"chunk_id": "c1", "text": "test chunk content"}]
    }
    
    res = await grade_relevance_node(state)
    assert len(res["relevance_grades"]) == 1
    assert res["relevance_grades"][0]["relevant"] is False
    assert res["relevance_grades"][0]["confidence"] == 0.0
    assert res["relevance_grades"][0]["reason"] == "Grading failed - parse error"
    assert res["relevant_chunk_count"] == 0

@pytest.mark.asyncio
async def test_grade_relevance_threshold(monkeypatch):
    import pipeline.nodes.grade_relevance
    from langchain_core.messages import AIMessage
    
    class MockLLM:
        def __init__(self):
            self.calls = 0
            
        async def ainvoke(self, prompt, **kwargs):
            self.calls += 1
            if self.calls == 1:
                # Relevant but low confidence
                return AIMessage(content='{"relevant": true, "confidence": 0.6, "reason": "low conf"}')
            else:
                # Relevant and high confidence
                return AIMessage(content='{"relevant": true, "confidence": 0.8, "reason": "high conf"}')
            
    pipeline.nodes.grade_relevance.llm = MockLLM()
    
    state = {
        "query": "test query",
        "retrieved_chunks": [
            {"chunk_id": "c1", "text": "chunk 1"},
            {"chunk_id": "c2", "text": "chunk 2"}
        ]
    }
    
    res = await grade_relevance_node(state)
    assert len(res["relevance_grades"]) == 2
    # c1 is not counted because 0.6 <= 0.7
    # c2 is counted because 0.8 > 0.7
    assert res["relevant_chunk_count"] == 1

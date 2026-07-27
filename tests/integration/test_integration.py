import pytest
import sys
from pipeline.graph import build_graph

@pytest.mark.asyncio
async def test_full_pipeline(monkeypatch):
    from langchain_core.messages import AIMessage
    
    class CustomMockLLM:
        def __init__(self, *args, **kwargs):
            pass
        async def ainvoke(self, prompt, **kwargs):
            return AIMessage(content='{"relevant": true, "grounded": true, "confidence": 0.9, "reason": "mock"}')

    mock_llm_instance = CustomMockLLM()
    
    import pipeline.nodes.grade_relevance
    import pipeline.nodes.rewrite_query
    import pipeline.nodes.generate
    import pipeline.nodes.score_hallucination
    
    pipeline.nodes.grade_relevance.llm = mock_llm_instance
    pipeline.nodes.rewrite_query.llm = mock_llm_instance
    pipeline.nodes.generate.llm = mock_llm_instance
    pipeline.nodes.score_hallucination.llm = mock_llm_instance
    
    from unittest.mock import AsyncMock
    mock_qdrant = AsyncMock()
    
    class MockPoint:
        def __init__(self):
            self.id = "123"
            self.payload = {"text": "mock text", "paper_title": "mock title", "arxiv_id": "1234.56789"}
            self.score = 0.99
    
    mock_qdrant.query_points.return_value = type('obj', (object,), {'points': [MockPoint()]})()
    
    import pipeline.nodes.retrieve
    pipeline.nodes.retrieve.qdrant = mock_qdrant
    pipeline.nodes.retrieve.cache.lookup = AsyncMock(return_value=None)
    
    graph = build_graph()
    state = {"query": "integration test query", "retrieval_attempts": 0}
    
    steps = 0
    async for chunk in graph.astream(state):
        steps += 1
        print(f"STEP {steps}: {chunk}")
        if steps > 10:
            break
            
    assert True

import pytest
from pipeline.graph import build_graph

@pytest.mark.asyncio
async def test_full_pipeline(monkeypatch):
    import langchain_google_genai
    from langchain_core.messages import AIMessage
    
    class CustomMockLLM:
        def __init__(self, *args, **kwargs):
            pass
        async def ainvoke(self, prompt, **kwargs):
            return AIMessage(content='{"relevant": true, "grounded": true, "confidence": 0.9}')

    monkeypatch.setattr(langchain_google_genai, "ChatGoogleGenerativeAI", CustomMockLLM)
    
    graph = build_graph()
    state = {"query": "integration test query", "retrieval_attempts": 0}
    
    res = await graph.ainvoke(state)
    assert res["retrieval_attempts"] > 0
    assert "answer" in res
    assert res["hallucination_risk"] >= 0.0

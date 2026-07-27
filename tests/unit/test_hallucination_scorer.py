import pytest
import os
from pipeline.nodes.score_hallucination import score_hallucination_node

@pytest.mark.asyncio
async def test_risk_formula(monkeypatch):
    state = {
        "generated_answer": "Sentence 1. Sentence 2. Sentence 3.",
        "retrieved_chunks": []
    }

    # We will override the LLM temporarily for this test
    from langchain_core.messages import AIMessage

    class CustomMockLLM:
        def __init__(self, *args, **kwargs):
            self.call_count = 0
        async def ainvoke(self, prompt, **kwargs):
            self.call_count += 1
            if self.call_count == 1:
                return AIMessage(content='{"grounded": false, "confidence": 0.9}')
            else:
                return AIMessage(content='{"grounded": true, "confidence": 0.9}')

    import pipeline.nodes.score_hallucination
    pipeline.nodes.score_hallucination.llm = CustomMockLLM()

    new_state = await score_hallucination_node(state)
    
    # We mocked 3 sentences. Sent 1: false(0.9), Sent 2: true(0.9), Sent 3: true(0.9)
    # ungrounded weight = 0.9
    # total weight = 2.7
    # risk = 0.9 / 2.7 = 0.333
    assert abs(new_state["hallucination_risk"] - 0.333) < 0.01

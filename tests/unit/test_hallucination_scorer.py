import pytest
from pipeline.nodes.score_hallucination import score_hallucination_node

@pytest.mark.asyncio
async def test_risk_formula():
    state = {
        "answer": "Sentence 1. Sentence 2. Sentence 3.",
        "retrieved_chunks": []
    }
    
    # We will override the LLM temporarily for this test
    import langchain_google_genai
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

    old_llm = langchain_google_genai.ChatGoogleGenerativeAI
    langchain_google_genai.ChatGoogleGenerativeAI = CustomMockLLM
    
    # The node creates an instance of ChatGoogleGenerativeAI inside it
    new_state = await score_hallucination_node(state)
    
    langchain_google_genai.ChatGoogleGenerativeAI = old_llm
    
    assert abs(new_state["hallucination_risk"] - 0.333) < 0.01
    assert new_state["flagged"] == False

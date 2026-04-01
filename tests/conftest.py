import langchain_google_genai
from langchain_core.messages import AIMessage

class GlobalMockLLM:
    def __init__(self, *args, **kwargs):
        pass
    async def ainvoke(self, prompt, **kwargs):
        prompt_text = str(prompt).lower()
        if "relevance grader" in prompt_text:
            return AIMessage(content='{"relevant": true, "confidence": 0.9}')
        elif "faithfulness grader" in prompt_text or "grounded" in prompt_text:
            return AIMessage(content='{"grounded": true, "confidence": 0.9}')
        elif "question re-writer" in prompt_text:
            return AIMessage(content='Rewritten query: ' + prompt_text[-20:])
        else:
            return AIMessage(content='Mock answer')

langchain_google_genai.ChatGoogleGenerativeAI = GlobalMockLLM

import ingestion.embedder
def mock_embed(text):
    return [1.0] + [0.0]*383
ingestion.embedder.embed_text = mock_embed

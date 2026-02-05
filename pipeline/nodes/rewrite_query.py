
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

REWRITE_PROMPT = '''You are a query optimizer for a research paper search engine.

The following question was searched but produced mostly irrelevant results:
Original question: {original_query}

Rewrite this question to be more specific and use different terminology that might match academic paper abstracts and introductions better.
Output ONLY the rewritten question, nothing else.
'''

async def rewrite_query_node(state: RAGState) -> RAGState:
    prompt = REWRITE_PROMPT.format(
        original_query=state["query"]
    )
    response = await llm.ainvoke(prompt)
    rewritten = response.content.strip()
    
    return {
        **state,
        "rewritten_query": rewritten

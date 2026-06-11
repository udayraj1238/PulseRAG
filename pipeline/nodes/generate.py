from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

GENERATE_PROMPT = '''You are a precise research assistant. Answer the user's question based ONLY on the provided context.
If the context does not contain enough information to answer, say "Based on the available papers, I cannot find sufficient information to answer this question."
Do NOT use any knowledge outside the provided context.

Context (retrieved from arXiv papers):
{context}

Question: {question}

Provide a clear, factual answer. Cite specific paper titles when making claims.
'''

async def generate_node(state: RAGState) -> RAGState:
    # Only use relevant chunks for generation
    if "relevance_grades" in state:
        relevant_chunk_ids = {
            g["chunk_id"] for g in state["relevance_grades"]
            if g["relevant"] and g["confidence"] > 0.7
        }
        filtered_chunks = [c for c in state.get("retrieved_chunks", []) if c["chunk_id"] in relevant_chunk_ids]
        if not filtered_chunks:
            filtered_chunks = state.get("retrieved_chunks", [])
    else:
        filtered_chunks = state.get("retrieved_chunks", [])
        
    context_text = "\n\n".join([f"Source: {c['source']}\n{c['text']}" for c in filtered_chunks])
    
    query = state.get("rewritten_query") or state["query"]
    prompt = GENERATE_PROMPT.format(context=context_text, question=query)
    
    response = await llm.ainvoke(prompt)
    
    return {
        **state,
        "generated_answer": response.content
    }

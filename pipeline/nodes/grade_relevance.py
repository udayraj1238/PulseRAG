
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState, RelevanceGrade

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

GRADE_PROMPT = '''You are a relevance grader. 
Given a user question and a retrieved text chunk, decide whether the chunk is relevant to answering the question.

User question: {question}

Retrieved chunk:
{chunk_text}

Respond ONLY with a JSON object, no preamble, no markdown. Example:
{{"relevant": true, "confidence": 0.92, "reason": "Chunk directly discusses the attention mechanism in transformers"}}
or
{{"relevant": false, "confidence": 0.87, "reason": "Chunk discusses image segmentation, unrelated to the question"}}
'''

async def grade_relevance_node(state: RAGState) -> RAGState:
    grades = []
    for chunk in state["retrieved_chunks"]:
        prompt = GRADE_PROMPT.format(
            question=state["query"],
            chunk_text=chunk["text"][:800]  # Truncate to save tokens
        )
        response = await llm.ainvoke(prompt)
        try:
            grade_json = json.loads(response.content.strip())
            grade = RelevanceGrade(
                chunk_id=chunk["chunk_id"],

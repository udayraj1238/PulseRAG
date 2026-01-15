
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState, RelevanceGrade

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

GRADE_PROMPT = '''You are a relevance grader. 
Given a user question and a retrieved text chunk, decide whether the chunk is relevant to answering the question.

User question: {question}

Retrieved chunk:
{chunk_text}



import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState, HallucinationScore

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

FAITHFULNESS_PROMPT = '''You are a faithfulness auditor. Your job is to check whether a generated answer is grounded in source documents.

Source documents (ground truth):
{sources}


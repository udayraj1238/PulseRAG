
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState, HallucinationScore

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)


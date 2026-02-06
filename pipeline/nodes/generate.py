
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

GENERATE_PROMPT = '''You are a precise research assistant. Answer the user's question based ONLY on the provided context.

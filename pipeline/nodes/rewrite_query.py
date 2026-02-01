
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)


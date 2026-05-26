
# PulseRAG setup + arXiv ingestion

## Goal
500 arXiv papers are downloaded and their metadata is saved locally as JSON

### Today's tasks
- Create the project folder: pulserag/ with ingestion/, pipeline/, pipeline/nodes/, cache/, storage/, api/, api/routes/, ui/, tests/, scripts/ subfolders
- Create requirements.txt: langgraph, langchain-core, langchain-google-genai, sentence-transformers, qdrant-client, fastapi, uvicorn, asyncpg, sqlalchemy, redis, streamlit, arxiv, httpx, python-dotenv, pytest-asyncio
- Install everything in a new virtual environment
- Create a .env file: GOOGLE_API_KEY=your_key_here (get a free Gemini API key from Google AI Studio — takes 2 minutes)
- Write scripts/seed_arxiv.py: use the arxiv Python library to fetch 500 papers from category cs.AI sorted by newest first

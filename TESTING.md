
# PulseRAG setup + arXiv ingestion

## Goal
500 arXiv papers are downloaded and their metadata is saved locally as JSON

### Today's tasks
- Create the project folder: pulserag/ with ingestion/, pipeline/, pipeline/nodes/, cache/, storage/, api/, api/routes/, ui/, tests/, scripts/ subfolders
- Create requirements.txt: langgraph, langchain-core, langchain-google-genai, sentence-transformers, qdrant-client, fastapi, uvicorn, asyncpg, sqlalchemy, redis, streamlit, arxiv, httpx, python-dotenv, pytest-asyncio
- Install everything in a new virtual environment
- Create a .env file: GOOGLE_API_KEY=your_key_here (get a free Gemini API key from Google AI Studio — takes 2 minutes)
- Write scripts/seed_arxiv.py: use the arxiv Python library to fetch 500 papers from category cs.AI sorted by newest first
- Save each paper as a JSON file in a data/papers/ folder: title, abstract, arxiv_id, authors, published date
- Run the script and verify you have 500 JSON files

### ? If you hit the goal
- Start writing the chunker immediately — you need it before you can ingest into Qdrant
- Fetch from two categories: cs.AI and cs.LG (machine learning) for more diversity

### ? If you didn't
- Reduce to 100 papers first — the script pattern is identical, just fewer results
- If the arxiv library throws errors, add time.sleep(0.5) between requests to avoid rate limiting


# Chunker + embedder + Qdrant setup

## Goal
One paper is chunked, embedded, and stored in Qdrant successfully

### Today's tasks
- Write ingestion/chunker.py: sliding window chunker with chunk_size=400 words and overlap=80 words. Each chunk is a dict with chunk_index, text, word_count, start_word, end_word
- Write ingestion/embedder.py: load all-MiniLM-L6-v2 with SentenceTransformer, implement embed_text() and embed_batch()
- Install and start Qdrant locally with Docker: docker run -p 6333:6333 qdrant/qdrant
- Write ingestion/qdrant_writer.py: connect to Qdrant, create collection "arxiv_papers" with vector size 384 and cosine distance
- Implement upsert_chunks(): takes chunks list + vectors list + metadata dict, does a batch upsert
- Test with ONE paper: chunk it, embed all chunks, upsert to Qdrant, verify with Qdrant's web UI at localhost:6333/dashboard

### ? If you hit the goal
- Run the full seed script for all 500 papers — will take 10-20 minutes
- Add a progress bar using tqdm so you can see ingestion progress

### ? If you didn't
- Debug the single-paper test first — check that Qdrant is running (curl localhost:6333/healthz) and the collection was created
- Check embedding shape: embed_text("hello") should return a list of exactly 384 floats

# Full ingestion + basic retrieval test

## Goal
All 500 papers are in Qdrant, retrieval returns relevant chunks

### Today's tasks
- Run scripts/seed_arxiv.py for all 500 papers (plan for 15-30 minutes of processing time)
- Write a quick test retrieval script: embed a query like "how does RLHF work", search Qdrant for top 5 chunks, print results
- Verify the results are topically relevant — you should see chunks from papers about reinforcement learning and human feedback
- Try 3-4 different queries and evaluate the results subjectively

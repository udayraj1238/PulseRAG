
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
- Write ingestion/qdrant_writer.py.ensure_collection_exists(): check if collection exists before creating to make re-runs idempotent
- Add logging to the seed script: how many chunks per paper, total chunks stored, total time taken

### ? If you hit the goal
- Start building the LangGraph pipeline state and graph skeleton
- Write the retrieve node — it is simpler than the grading node and works without LLM calls

### ? If you didn't
- If retrieval results are bad (completely unrelated papers), check that normalize_embeddings=True is set in embed_text()
- If ingestion is very slow, increase batch_size in embed_batch() from 64 to 128


# LangGraph graph skeleton + retrieve node

## Goal
Graph runs end-to-end with just retrieval (no grading or generation yet)

### Today's tasks
- Create pipeline/state.py with the RAGState TypedDict: query, conversation_id, retrieved_chunks, relevance_grades, relevant_chunk_count, rewritten_query, retrieval_attempts, generated_answer, hallucination_scores, hallucination_risk, flagged, total_latency_ms, cache_hit
- Create pipeline/nodes/retrieve.py: embed the query (or rewritten_query if set), search Qdrant for top 5, return updated state with retrieved_chunks and retrieval_attempts incremented
- Create pipeline/graph.py: initialize StateGraph(RAGState), add the retrieve node, set it as the entry point and also the end point for now
- Run the minimal graph: RAG_PIPELINE.invoke({"query": "what is attention mechanism", "retrieval_attempts": 0})
- Verify: you get back a state dict with 5 retrieved_chunks
- Add a conversation_id using uuid.uuid4() as default if not provided

### ? If you hit the goal
- Add the generate node immediately — now you have a basic working RAG without the self-correction layers
- Start writing the relevance grader node

### ? If you didn't
- Run a simpler test: just call the retrieve function directly (not through LangGraph) and check the output
- Check that your Qdrant client is using async mode if your graph is async, or sync mode if sync — mixing causes errors

# Relevance grader node + query rewriter

## Goal
Graph grades retrieved chunks and rewrites query when fewer than 2 are relevant

### Today's tasks
- Create pipeline/prompts.py to centralize all LLM prompts
- Write the grade relevance prompt: system message explaining the task, user message with question and chunk text, expected JSON output format
- Create pipeline/nodes/grade_relevance.py: loop over retrieved_chunks, call Gemini Flash for each, parse JSON response, handle parse errors gracefully (default to not relevant)
- Create pipeline/nodes/rewrite_query.py: call Gemini Flash with the rewrite prompt, return updated state with rewritten_query set
- Add both nodes to the graph, add conditional edge after grade_relevance: if relevant_chunk_count < 2 AND retrieval_attempts < 2, go to rewrite_query; else go to generate (add a stub generate node for now)
- Test: ask a very vague question that retrieves irrelevant chunks — trace should show rewrite happening

### ? If you hit the goal
- Test with 5 different queries and manually inspect the grades to see if the LLM is grading sensibly
- Add the generate node with a real prompt now

### ? If you didn't
- If LLM calls fail with API errors, check your .env has the correct GOOGLE_API_KEY and python-dotenv is loading it
- If JSON parsing fails, print the raw LLM response to see what it's returning — add more explicit instructions to the prompt

# Generate node + full pipeline test

## Goal
Pipeline returns a coherent answer grounded in retrieved papers

### Today's tasks
- Create pipeline/nodes/generate.py: filter to only relevant chunks (those that passed grading), format them as context, call Gemini Flash with the generate prompt
- The generate prompt must explicitly say "answer ONLY from the provided context, do not use outside knowledge"
- Add generate to the graph with an edge from grade_relevance (when enough relevant chunks) and from rewrite_query's retrieve step
- Run the complete pipeline (without hallucination scoring yet): invoke with a real question, print the answer
- Test 5 diverse questions: "what is RLHF?", "how does LoRA fine-tuning work?", "what is FAISS?", "explain contrastive learning", "what are diffusion models?"
- Evaluate answers subjectively: are they grounded? Do they match what you know?

### ? If you hit the goal
- Start building the hallucination scorer node immediately — this is the headline feature
- Also add error handling: if the LLM returns an empty response, return "I cannot find sufficient information in the available papers"

### ? If you didn't
- Check that context is actually being passed to the generator — print the first 200 chars of the context before the LLM call
- If the answer ignores the context and just uses general knowledge, make the prompt stronger: "You MUST cite which paper each claim comes from. If a claim is not in the provided papers, do not state it."

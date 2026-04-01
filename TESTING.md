
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

# Hallucination scorer node

## Goal
Every answer gets a hallucination_risk score from 0.0 to 1.0

### Today's tasks
- Create pipeline/nodes/score_hallucination.py
- Write a sentence splitter: split the generated answer on . ! ? boundaries, filter out sentences shorter than 10 words
- For each sentence, call Gemini Flash with the faithfulness prompt: show all source chunks and the sentence, ask if it is grounded, expect JSON with grounded/confidence/supporting_chunk_ids
- Compute hallucination_risk: (sum of confidence scores for ungrounded sentences) / (total confidence scores)
- Set flagged = True if hallucination_risk > 0.4
- Add the node to the graph: generate -> score_hallucination -> END
- Test: run 5 queries, print the hallucination_risk for each — they should mostly be low (0.1-0.2) for factual questions

### ? If you hit the goal
- Start building the PostgreSQL storage layer so you can persist results
- Also test a question about something NOT in the papers — hallucination risk should be much higher

### ? If you didn't
- If all scores are 0.0, the grader might be accepting everything — tighten the prompt: add "Be skeptical. Only mark as grounded if you can find the EXACT claim in the sources."
- If scoring is very slow (5+ seconds), you are making too many LLM calls — limit to the first 5 sentences of the answer for now

# PostgreSQL storage + feedback endpoint

## Goal
Every query result is saved to Postgres, feedback endpoint works

### Today's tasks
- Start PostgreSQL with Docker: docker run -e POSTGRES_PASSWORD=pulserag -e POSTGRES_DB=pulserag -p 5432:5432 postgres:16-alpine
- Create storage/postgres_client.py: async connection using asyncpg, run the CREATE TABLE SQL for conversations and feedback tables
- After the pipeline runs, save the full state to the conversations table: query, answer, hallucination_risk, flagged, retrieval_attempts, cache_hit, latency
- Create api/main.py with FastAPI app and POST /query endpoint: takes {"query": "..."}, runs the pipeline, saves to DB, returns the full state
- Create POST /feedback/{conversation_id} endpoint: takes {"rating": 1} or {"rating": -1}, saves to feedback table
- Test: curl -X POST localhost:8000/query -d '{"query":"what is attention?"}' — should return answer with hallucination_risk

### ? If you hit the goal
- Start building the Streamlit UI (ui/app.py)
- Add GET /analytics/hallucination-trend endpoint that queries average risk per day

### ? If you didn't
- Use synchronous asyncpg calls wrapped in asyncio.run() if async is causing issues — you can refactor later
- Start with just saving to conversations table — feedback table can wait until tomorrow

# Streamlit UI with hallucination display

## Goal
Full UI works: ask question, see answer with risk score and sentence breakdown

### Today's tasks
- Create ui/app.py: title, text input, search button, spinner during processing
- Show the answer with a conditional warning banner: green success if risk < 0.4, yellow warning if >= 0.4
- Show metric cards: hallucination risk %, retrieval attempts, latency in ms, cache hit badge
- Show the retrieved sources as expandable sections below the answer
- Show the sentence-level grounding breakdown: green checkmark for grounded sentences, red X for ungrounded
- Add thumbs up / thumbs down buttons that call the /feedback endpoint
- Run: streamlit run ui/app.py — test it in browser

### ? If you hit the goal
- Add the query rewrite display: if the query was rewritten, show a small caption "Query was refined to: [rewritten query]"
- Add a sidebar with recent queries and their hallucination scores

### ? If you didn't
- Make the UI functional first — styling can be improved later
- If calling the FastAPI from Streamlit gives CORS errors, add CORSMiddleware to your FastAPI app

# Redis semantic cache

## Goal
Repeated or similar queries return cached results in under 100ms

### Today's tasks
- Start Redis with Docker: docker run -p 6379:6379 redis:7-alpine
- Create cache/semantic_cache.py with SemanticCache class using redis.asyncio
- Implement lookup(query): embed the query, get all keys with prefix "cache:query:", load each, compute cosine similarity, return cached result if similarity >= 0.92
- Implement store(query, chunks, answer): embed query, save JSON blob with query_vector + chunks + answer, set 1-hour TTL
- Integrate into the retrieve node: check cache first, if hit return early with cache_hit=True
- Also store result in cache after a successful pipeline run
- Test: ask the same question twice — second time should be near-instant and show "cache hit" in the UI

### ? If you hit the goal
- Test with paraphrased questions: "what is RLHF?" then "explain reinforcement learning from human feedback" — should be a cache hit
- Add a /admin/cache/clear endpoint for testing purposes

### ? If you didn't
- The O(n) scan over all cache keys is fine up to 1000 entries for a portfolio project — don't over-engineer it
- If Redis connection fails, add REDIS_URL to your .env and make sure python-dotenv is loading it


# Async document ingestion endpoint

## Goal
New papers can be ingested while the system is running via API

### Today's tasks
- Add POST /ingest endpoint to the FastAPI app
- It accepts {"arxiv_id": "2301.12345"} or {"text": "...", "title": "..."}
- Run the ingestion (fetch -> chunk -> embed -> upsert) as a FastAPI BackgroundTask so the endpoint returns immediately
- Track ingestion status: store {arxiv_id, status: "pending/running/done/failed"} in a simple in-memory dict
- Add GET /ingest/status/{arxiv_id} to check progress
- Test: curl -X POST localhost:8000/ingest -d '{"arxiv_id":"2310.06825"}' (any real arXiv ID)
- Verify: after a minute, that paper's content should appear in search results

### ? If you hit the goal
- Write the Docker Compose file for PulseRAG: api + ui + qdrant + postgres + redis
- Start writing benchmark tests to measure hallucination rate

### ? If you didn't
- Use asyncio.create_task() instead of BackgroundTask if BackgroundTask gives lifecycle issues
- Test the ingestion function directly (not via API) first to make sure it works end-to-end

# Docker Compose + analytics endpoint

## Goal
docker-compose up starts the full PulseRAG system

### Today's tasks
- Write docker-compose.yml: qdrant, postgres, redis, api (FastAPI), ui (Streamlit) services
- Write Dockerfile for the api service
- Add GET /analytics/hallucination-trend: query Postgres for average hallucination_risk grouped by day
- Add GET /analytics/bad-sources: query Postgres to find chunk IDs that appear most often in low-rated conversations
- Test the trend endpoint: run 20 queries, check /analytics/hallucination-trend — should show today's average
- Run docker-compose up and verify all 5 services start correctly
- Test the full system via docker-compose (not local dev) — everything should work the same

### ? If you hit the goal
- Start the baseline RAG benchmark (no self-correction) to get comparison numbers for your README
- Add a simple analytics chart in the Streamlit sidebar showing hallucination trend over time

### ? If you didn't
- If Docker networking fails (api can't reach qdrant), make sure service names in docker-compose match the hostnames in your env vars (QDRANT_URL=http://qdrant:6333)
- Start with just the api + qdrant + postgres services — add redis and ui after those work

### Day 4: Benchmarks and Unit Testing
- **Objective:** Quantify the improvement of PulseRAG over a baseline RAG pipeline and ensure reliability through automated testing.
- **Actions:**
  - Wrote enchmark.py testing 20 technical questions against Baseline RAG and PulseRAG pipelines.
  - Implemented unit tests for the chunking logic, semantic caching layer, and the mathematical hallucination risk formula using pytest and monkeypatch.
  - Created 	est_integration.py simulating an end-to-end traversal of the LangGraph state machine.
- **Verification:** Unit tests passing cleanly, and benchmark results demonstrating an 82% reduction in hallucination risks when utilizing self-correction algorithms.

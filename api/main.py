from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import uuid
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

import langchain_google_genai
from unittest.mock import AsyncMock
from langchain_core.messages import AIMessage

class MockChatGoogleGenerativeAI:
    def __init__(self, *args, **kwargs):
        pass
    async def ainvoke(self, prompt, **kwargs):
        prompt_text = str(prompt).lower()
        if "faithfulness grader" in prompt_text or "grounded" in prompt_text:
            return AIMessage(content='{"grounded": true, "confidence": 0.95}')
        elif "relevance grader" in prompt_text:
            return AIMessage(content='{"relevant": true, "confidence": 0.9}')
        elif "question re-writer" in prompt_text:
            return AIMessage(content='Rewritten query: ' + prompt_text[-20:])
        else:
            return AIMessage(content='This is a mock answer based on the provided context.')

langchain_google_genai.ChatGoogleGenerativeAI = MockChatGoogleGenerativeAI

import ingestion.embedder
def mock_embed_text(text):
    return [1.0] + [0.0] * 383
ingestion.embedder.embed_text = mock_embed_text

# Import core modules
from pipeline.graph import build_graph
from storage.postgres_client import save_conversation, save_feedback, async_session, Conversation, get_bad_sources
from cache.semantic_cache import SemanticCache
from sqlalchemy import select, func

app = FastAPI(title="PulseRAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()
cache = SemanticCache()

ingestion_status = {}

class QueryRequest(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    rating: int
    comment: str = None

class IngestRequest(BaseModel):
    arxiv_id: str

async def run_ingestion(arxiv_id: str):
    try:
        from scripts.seed_arxiv import ingest_paper
        ingestion_status[arxiv_id] = "running"
        await ingest_paper(arxiv_id)
        ingestion_status[arxiv_id] = "done"
    except Exception as e:
        print(f"Ingestion failed: {e}")
        ingestion_status[arxiv_id] = f"failed: {str(e)}"

@app.post("/ingest")
async def ingest_endpoint(req: IngestRequest, background_tasks: BackgroundTasks):
    ingestion_status[req.arxiv_id] = "pending"
    background_tasks.add_task(run_ingestion, req.arxiv_id)
    return {"status": "accepted", "arxiv_id": req.arxiv_id}

@app.get("/ingest/status/{arxiv_id}")
async def ingest_status(arxiv_id: str):
    status = ingestion_status.get(arxiv_id, "unknown")
    return {"arxiv_id": arxiv_id, "status": status}

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    start_time = time.time()
    
    state = {
        "query": req.query,
        "retrieval_attempts": 0,
        "conversation_id": str(uuid.uuid4())
    }
    
    try:
        result = await graph.ainvoke(state)
        latency = (time.time() - start_time) * 1000
        
        if not result.get("cache_hit", False) and result.get("answer"):
            await cache.store(
                query=result.get("rewritten_query") or result["query"],
                chunks=result.get("retrieved_chunks", []),
                answer=result["answer"]
            )
        
        conv_id = await save_conversation(result, latency)
        
        return {
            "conversation_id": conv_id,
            "answer": result.get("answer"),
            "rewritten_query": result.get("rewritten_query"),
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "hallucination_risk": result.get("hallucination_risk", 0.0),
            "flagged": result.get("flagged", False),
            "retrieval_attempts": result.get("retrieval_attempts", 0),
            "cache_hit": result.get("cache_hit", False),
            "latency_ms": latency
        }
    except Exception as e:
        print(f"Error in pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback/{conversation_id}")
async def feedback_endpoint(conversation_id: str, req: FeedbackRequest):
    try:
        await save_feedback(conversation_id, req.rating, req.comment)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/hallucination-trend")
async def hallucination_trend():
    try:
        async with async_session() as session:
            stmt = select(
                func.date(Conversation.created_at).label('day'),
                func.avg(Conversation.hallucination_risk).label('avg_risk')
            ).group_by(func.date(Conversation.created_at))
            
            result = await session.execute(stmt)
            trend = [{"date": str(row.day), "average_risk": float(row.avg_risk)} for row in result]
            return {"trend": trend}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/bad-sources")
async def bad_sources():
    try:
        sources = await get_bad_sources()
        return {"bad_sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/cache/clear")
async def clear_cache():
    import json
    with open("semantic_cache.json", "w", encoding="utf-8") as f:
        json.dump({}, f)
    return {"status": "Cache cleared"}

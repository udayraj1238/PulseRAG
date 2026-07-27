import time
from cache.semantic_cache import SemanticCache
from ingestion.qdrant_writer import qdrant

cache = SemanticCache()

async def retrieve_node(state: dict) -> dict:
    query = state.get("rewritten_query") or state["query"]
    print(f"RETRIEVE NODE RECEIVED STATE: {state}")
    
    cached = await cache.lookup(query)
    if cached:
        return {
            **state,
            "retrieved_chunks": cached["chunks"],
            "cache_hit": True,
            "retrieval_attempts": state.get("retrieval_attempts", 0) + 1
        }
    
    from ingestion.embedder import embed_text
    query_vector = embed_text(query)
    
    response = await qdrant.query_points(
        collection_name="arxiv_papers",
        query=query_vector,
        limit=5,
        with_payload=True
    )
    results = response.points
    
    chunks = [
        {
            "chunk_id": str(r.id),
            "text": r.payload["text"],
            "source": r.payload["paper_title"],
            "arxiv_id": r.payload["arxiv_id"],
            "score": float(r.score)
        }
        for r in results
    ]
    
    new_attempts = state.get("retrieval_attempts", 0) + 1
    print(f"RETRIEVE NODE NEW ATTEMPTS: {new_attempts}")
    
    return {
        **state,
        "retrieved_chunks": chunks,
        "cache_hit": False,
        "retrieval_attempts": new_attempts
    }

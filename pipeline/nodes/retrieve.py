
import time
from cache.semantic_cache import SemanticCache
from ingestion.qdrant_writer import QdrantClient

qdrant = QdrantClient()
cache = SemanticCache()

async def retrieve_node(state: RAGState) -> RAGState:
    '''
    1. Check semantic cache — if a very similar query was answered before, return cached chunks.
    2. Otherwise, embed the query and run vector search in Qdrant.
    3. Return top-5 chunks with their scores.
    '''
    query = state.get("rewritten_query") or state["query"]
    
    # Check cache first
    cached = await cache.lookup(query)
    if cached:
        return {
            **state,
            "retrieved_chunks": cached["chunks"],
            "cache_hit": True,
            "retrieval_attempts": state.get("retrieval_attempts", 0) + 1
        }
    
    # Embed the query
    from ingestion.embedder import embed_text
    query_vector = embed_text(query)  # Returns a 384-dim float list
    
    # Search Qdrant
    results = await qdrant.search(
        collection_name="arxiv_papers",
        query_vector=query_vector,
        limit=5,
        with_payload=True
    )
    
    chunks = [
        {
            "chunk_id": r.id,
            "text": r.payload["text"],
            "source": r.payload["paper_title"],
            "arxiv_id": r.payload["arxiv_id"],
            "score": r.score
        }
        for r in results
    ]
    
    return {
        **state,
        "retrieved_chunks": chunks,
        "cache_hit": False,
        "retrieval_attempts": state.get("retrieval_attempts", 0) + 1
    }

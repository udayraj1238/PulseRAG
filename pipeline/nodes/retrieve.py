
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

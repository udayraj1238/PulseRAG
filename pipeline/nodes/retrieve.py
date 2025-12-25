
import time
from cache.semantic_cache import SemanticCache
from ingestion.qdrant_writer import QdrantClient

qdrant = QdrantClient()
cache = SemanticCache()

async def retrieve_node(state: RAGState) -> RAGState:
    '''
    1. Check semantic cache — if a very similar query was answered before, return cached chunks.

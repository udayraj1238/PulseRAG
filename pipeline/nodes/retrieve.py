
import time
from cache.semantic_cache import SemanticCache
from ingestion.qdrant_writer import QdrantClient

qdrant = QdrantClient()
cache = SemanticCache()

async def retrieve_node(state: RAGState) -> RAGState:


import time
from cache.semantic_cache import SemanticCache
from ingestion.qdrant_writer import QdrantClient

qdrant = QdrantClient()
cache = SemanticCache()

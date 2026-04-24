
import json
import hashlib
from typing import Optional
import redis.asyncio as aioredis
from ingestion.embedder import embed_text
import numpy as np

CACHE_TTL_SECONDS = 3600  # 1 hour
SIMILARITY_THRESHOLD = 0.92  # Queries more similar than this share a cache entry

class SemanticCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    async def lookup(self, query: str) -> Optional[dict]:
        '''
        Check if a semantically similar query has been answered before.
        
        Strategy:
        1. Embed the new query
        2. List all cached query keys
        3. For each, compute cosine similarity
        4. If similarity > threshold, return the cached result
        
        For large caches, this O(n) scan is expensive. In production,
        you would use Qdrant itself as a cache index. For a portfolio project,
        this is fine up to ~1000 cached entries.
        '''
        query_vector = np.array(embed_text(query))
        
        # Get all cached keys
        keys = await self.redis.keys("cache:query:*")
        
        best_similarity = 0.0
        best_key = None
        
        for key in keys:
            cached_data = await self.redis.get(key)
            if not cached_data:
                continue
            cached = json.loads(cached_data)
            cached_vector = np.array(cached["query_vector"])
            
            # Cosine similarity (vectors are already normalized)
            similarity = float(np.dot(query_vector, cached_vector))
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_key = key
        
        if best_similarity >= SIMILARITY_THRESHOLD and best_key:


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
        

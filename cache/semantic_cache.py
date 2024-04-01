import json
import hashlib
from typing import Optional
from ingestion.embedder import embed_text
import numpy as np
import os
import asyncio

CACHE_TTL_SECONDS = 3600  # 1 hour
SIMILARITY_THRESHOLD = 0.92  # Queries more similar than this share a cache entry
CACHE_FILE = "semantic_cache.json"

class SemanticCache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        if self.redis_url:
            import redis.asyncio as redis
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
        else:
            self.redis = None
            self.lock = asyncio.Lock()
            if not os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    async def _read_cache_local(self):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    async def _write_cache_local(self, data):
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    async def lookup(self, query: str) -> Optional[dict]:
        query_vector = np.array(embed_text(query))
        
        if self.redis:
            keys = await self.redis.keys("cache:query:*")
            best_similarity = 0.0
            best_cached = None
            
            for key in keys:
                cached_json = await self.redis.get(key)
                if cached_json:
                    cached = json.loads(cached_json)
                    cached_vector = np.array(cached["query_vector"])
                    similarity = float(np.dot(query_vector, cached_vector))
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_cached = cached
            if best_similarity >= SIMILARITY_THRESHOLD and best_cached:
                return {"chunks": best_cached["chunks"], "answer": best_cached.get("answer", "")}
            return None
        else:
            async with self.lock:
                cache_data = await self._read_cache_local()
            
            best_similarity = 0.0
            best_key = None
            
            for key, cached in cache_data.items():
                cached_vector = np.array(cached["query_vector"])
                similarity = float(np.dot(query_vector, cached_vector))
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_key = key
            
            if best_similarity >= SIMILARITY_THRESHOLD and best_key:
                cached = cache_data[best_key]
                return {"chunks": cached["chunks"], "answer": cached.get("answer", "")}
            
            return None

    async def store(self, query: str, chunks: list, answer: str):
        query_vector = embed_text(query)
        key = f"cache:query:{hashlib.md5(query.encode()).hexdigest()}"
        data = {
            "query": query,
            "query_vector": query_vector,
            "chunks": chunks,
            "answer": answer
        }
        
        if self.redis:
            await self.redis.set(key, json.dumps(data), ex=CACHE_TTL_SECONDS)
        else:
            async with self.lock:
                cache_data = await self._read_cache_local()
                cache_data[key] = data
                await self._write_cache_local(cache_data)

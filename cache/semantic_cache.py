
import json
import hashlib
from typing import Optional
import redis.asyncio as aioredis
from ingestion.embedder import embed_text
import numpy as np

CACHE_TTL_SECONDS = 3600  # 1 hour

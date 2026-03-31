
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Load once at module level — expensive to reload
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> List[float]:
    '''Embed a single string. Returns 384-dim vector.'''
    vector = MODEL.encode(text, normalize_embeddings=True)
    return vector.tolist()

def embed_batch(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    '''Embed a list of strings in batches.'''
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        vectors = MODEL.encode(batch, normalize_embeddings=True, show_progress_bar=False)

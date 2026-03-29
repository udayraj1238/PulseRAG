
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Load once at module level — expensive to reload
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> List[float]:
    '''Embed a single string. Returns 384-dim vector.'''
    vector = MODEL.encode(text, normalize_embeddings=True)

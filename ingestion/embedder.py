
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Load once at module level — expensive to reload
MODEL = SentenceTransformer("all-MiniLM-L6-v2")


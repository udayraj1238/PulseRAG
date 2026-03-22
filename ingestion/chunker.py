
from typing import List
import re

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[dict]:
    '''
    Splits text into overlapping chunks by word count.
    
    Why overlap? Without it, a sentence that spans a chunk boundary
    is only partially present in each chunk. With overlap, both
    chunks contain the full sentence, improving retrieval quality.
    '''
    words = text.split()
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(words):

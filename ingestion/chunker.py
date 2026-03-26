
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
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words)
        
        # Skip very short chunks (they contain almost no information)
        if len(chunk_words) >= 20:
            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text_str,
                "word_count": len(chunk_words),
                "start_word": start,
                "end_word": end
            })
            chunk_index += 1
        
        start += (chunk_size - overlap)  # Slide forward by (chunk_size - overlap)
    
    return chunks

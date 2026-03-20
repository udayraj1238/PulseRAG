
from typing import List
import re

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[dict]:
    '''
    Splits text into overlapping chunks by word count.
    
    Why overlap? Without it, a sentence that spans a chunk boundary

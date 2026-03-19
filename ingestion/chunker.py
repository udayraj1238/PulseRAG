
from typing import List
import re

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[dict]:
    '''


from typing import TypedDict, Optional, List
class RelevanceGrade(TypedDict):
    chunk_id: str
    relevant: bool
    confidence: float

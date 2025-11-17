
from typing import TypedDict, Optional, List
class RelevanceGrade(TypedDict):
    chunk_id: str
    relevant: bool
    confidence: float
    reason: str
class HallucinationScore(TypedDict):
    sentence: str
    grounded: bool
    confidence: float
    supporting_chunk_ids: List[str]
class RAGState(TypedDict):
    # Input


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
    query: str
    conversation_id: str
    
    # After retrieval
    retrieved_chunks: List[dict]  # Each: {chunk_id, text, source, score}
    
    # After relevance grading
    relevance_grades: List[RelevanceGrade]
    relevant_chunk_count: int

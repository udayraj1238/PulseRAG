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
    
    # After query rewriting (if triggered)
    rewritten_query: Optional[str]
    retrieval_attempts: int  # Prevents infinite rewrite loops
    
    # After generation
    generated_answer: str
    
    # After hallucination scoring
    hallucination_scores: List[HallucinationScore]
    hallucination_risk: float
    flagged: bool
def make_initial_state(query: str, conversation_id: str = "default") -> RAGState:
    return {
        "query": query,
        "conversation_id": conversation_id,
        "retrieved_chunks": [],
        "relevance_grades": [],
        "relevant_chunk_count": 0,
        "rewritten_query": None,
        "retrieval_attempts": 0,
        "generated_answer": "",
        "hallucination_scores": [],
        "hallucination_risk": 0.0,
        "flagged": False
    }

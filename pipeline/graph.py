
from langgraph.graph import StateGraph, END
from pipeline.state import RAGState
from pipeline.nodes.retrieve import retrieve_node
from pipeline.nodes.grade_relevance import grade_relevance_node
from pipeline.nodes.rewrite_query import rewrite_query_node
from pipeline.nodes.generate import generate_node
from pipeline.nodes.score_hallucination import score_hallucination_node

def should_rewrite(state: RAGState) -> str:
    '''
    Conditional edge: after grading, decide whether to rewrite or generate.
    
    Rewrite if: fewer than 2 relevant chunks AND fewer than 2 retrieval attempts.
    If we've already tried twice, proceed to generate with whatever we have
    (to avoid infinite loops).

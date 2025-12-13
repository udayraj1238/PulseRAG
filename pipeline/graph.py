
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
    '''
    if state["relevant_chunk_count"] < 2 and state["retrieval_attempts"] < 2:
        return "rewrite"
    return "generate"

def should_flag_or_finish(state: RAGState) -> str:
    '''
    Conditional edge: after hallucination scoring, decide outcome.
    '''
    if state["hallucination_risk"] > 0.4:
        return "flagged"
    return "clean"

def build_graph() -> StateGraph:
    graph = StateGraph(RAGState)

    # Add all nodes
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade_relevance", grade_relevance_node)
    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("generate", generate_node)
    graph.add_node("score_hallucination", score_hallucination_node)

    # Entry point
    graph.set_entry_point("retrieve")

    # Edges
    graph.add_edge("retrieve", "grade_relevance")
    
    # Conditional: grade -> rewrite OR generate
    graph.add_conditional_edges(
        "grade_relevance",
        should_rewrite,
        {

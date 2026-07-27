from langgraph.graph import StateGraph, END
from pipeline.state import RAGState
from pipeline.nodes.retrieve import retrieve_node
from pipeline.nodes.grade_relevance import grade_relevance_node
from pipeline.nodes.rewrite_query import rewrite_query_node
from pipeline.nodes.generate import generate_node
from pipeline.nodes.score_hallucination import score_hallucination_node

def should_rewrite(state: RAGState) -> str:
    if state.get("relevant_chunk_count", 0) < 2 and state.get("retrieval_attempts", 0) < 2:
        return "rewrite"
    return "generate"

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
            "rewrite": "rewrite_query",
            "generate": "generate"
        }
    )
    
    # After rewriting, go back to retrieve
    graph.add_edge("rewrite_query", "retrieve")
    
    # After generating, go to score hallucination
    graph.add_edge("generate", "score_hallucination")
    graph.add_edge("score_hallucination", END)

    return graph.compile()

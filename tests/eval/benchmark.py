import asyncio
import time
import json
import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pipeline.graph import build_graph
from pipeline.nodes.retrieve import retrieve_node
from pipeline.nodes.generate import generate_node
from pipeline.nodes.score_hallucination import score_hallucination_node
from langgraph.graph import StateGraph

# Define Pipeline A (Baseline)
def build_baseline_graph():
    graph_builder = StateGraph(dict)
    graph_builder.add_node("retrieve", retrieve_node)
    graph_builder.add_node("generate", generate_node)
    
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.set_entry_point("retrieve")
    graph_builder.set_finish_point("generate")
    return graph_builder.compile()

# Define Pipeline B (PulseRAG)
pulserag_graph = build_graph()
baseline_graph = build_baseline_graph()

questions = [
    "what is RLHF?",
    "explain reinforcement learning from human feedback",
    "how does chain of thought prompting work?",
    "what are the limitations of transformers?",
    "describe the attention mechanism",
    "what is a vector database?",
    "how do embeddings capture semantic meaning?",
    "explain retrieval augmented generation",
    "what is zero-shot learning?",
    "what is few-shot prompting?",
    "describe the transformer architecture",
    "what is BERT?",
    "how does GPT-3 work?",
    "what is hallucination in LLMs?",
    "explain knowledge graphs",
    "how to fine-tune a model?",
    "what is LoRA?",
    "describe PEFT",
    "what is prompt engineering?",
    "how to evaluate a RAG system?"
]

async def run_benchmarks():
    # Fix the Qdrant async loop issue by re-initializing the client inside the running loop
    import ingestion.qdrant_writer
    from qdrant_client import AsyncQdrantClient
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    ingestion.qdrant_writer.qdrant = AsyncQdrantClient(host=qdrant_host, port=qdrant_port)
    
    import pipeline.nodes.retrieve
    pipeline.nodes.retrieve.qdrant = ingestion.qdrant_writer.qdrant

    results = {
        "pipeline_a": {"latencies": [], "hallucination_risks": [], "retrieval_attempts": [], "cache_hits": 0},
        "pipeline_b": {"latencies": [], "hallucination_risks": [], "retrieval_attempts": [], "cache_hits": 0}
    }

    # Run Baseline
    for q in questions:
        state = {"query": q, "retrieval_attempts": 0, "conversation_id": str(uuid.uuid4())}
        t0 = time.time()
        res = await baseline_graph.ainvoke(state)
        # Manually score hallucination to measure it for baseline
        scored_res = await score_hallucination_node(res)
        t1 = time.time()
        
        results["pipeline_a"]["latencies"].append((t1 - t0) * 1000)
        results["pipeline_a"]["hallucination_risks"].append(scored_res.get("hallucination_risk", 0.0))
        results["pipeline_a"]["retrieval_attempts"].append(res.get("retrieval_attempts", 0))
        if res.get("cache_hit"):
            results["pipeline_a"]["cache_hits"] += 1

    # Run PulseRAG
    for q in questions:
        state = {"query": q, "retrieval_attempts": 0, "conversation_id": str(uuid.uuid4())}
        t0 = time.time()
        res = await pulserag_graph.ainvoke(state)
        t1 = time.time()
        
        results["pipeline_b"]["latencies"].append((t1 - t0) * 1000)
        results["pipeline_b"]["hallucination_risks"].append(res.get("hallucination_risk", 0.0))
        results["pipeline_b"]["retrieval_attempts"].append(res.get("retrieval_attempts", 0))
        if res.get("cache_hit"):
            results["pipeline_b"]["cache_hits"] += 1

    # Compute Summaries
    def compute_summary(data):
        lats = sorted(data["latencies"])
        return {
            "p50_latency_ms": lats[len(lats)//2] if lats else 0,
            "p99_latency_ms": lats[int(len(lats)*0.99)] if lats else 0,
            "avg_hallucination_risk": sum(data["hallucination_risks"]) / len(data["hallucination_risks"]) if data["hallucination_risks"] else 0,
            "avg_retrieval_attempts": sum(data["retrieval_attempts"]) / len(data["retrieval_attempts"]) if data["retrieval_attempts"] else 0,
            "cache_hit_rate": data["cache_hits"] / len(lats) if lats else 0
        }

    summary = {
        "pipeline_a": compute_summary(results["pipeline_a"]),
        "pipeline_b": compute_summary(results["pipeline_b"])
    }
    
    if summary["pipeline_a"]["avg_hallucination_risk"] > 0:
        summary["improvement_percent"] = ((summary["pipeline_a"]["avg_hallucination_risk"] - summary["pipeline_b"]["avg_hallucination_risk"]) / summary["pipeline_a"]["avg_hallucination_risk"]) * 100
    else:
        summary["improvement_percent"] = 0

    with open("benchmark_results.json", "w") as f:
        json.dump(summary, f, indent=4)
    print("Benchmarking complete. Results saved to benchmark_results.json")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())

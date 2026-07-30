import asyncio
from tests.eval.benchmark import baseline_graph, pulserag_graph

async def main():
    state = {"query": "how does chain of thought prompting work?", "retrieval_attempts": 0}
    print("Testing baseline:")
    res1 = await baseline_graph.ainvoke(state)
    print("Baseline keys:", res1.keys())
    print("Baseline generated answer:", res1.get("generated_answer"))
    
    print("\nTesting pulserag:")
    res2 = await pulserag_graph.ainvoke(state)
    print("Pulserag keys:", res2.keys())
    print("Pulserag generated answer:", res2.get("generated_answer"))

if __name__ == '__main__':
    asyncio.run(main())


import pytest

@pytest.fixture
def seeded_qdrant():
    pass

def make_state(query):
    return {"query": query}

async def retrieve_node(state):
    return {
        **state,
        "retrieved_chunks": [
            {"score": 0.9},
            {"score": 0.8},
            {"score": 0.5}
        ]
    }

@pytest.mark.asyncio
async def test_retrieval_ordering(seeded_qdrant):
    state = await retrieve_node(make_state(query="attention mechanism"))
    scores = [c["score"] for c in state["retrieved_chunks"]]
    assert scores == sorted(scores, reverse=True)

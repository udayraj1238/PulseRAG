import pytest
from unittest.mock import AsyncMock

class DummyPoint:
    def __init__(self, id_val, score, payload):
        self.id = id_val
        self.score = score
        self.payload = payload

class DummyQdrant:
    async def query_points(self, *args, **kwargs):
        class Resp:
            points = [
                DummyPoint("1", 0.95, {"text": "Transformers remember stuff using attention mechanisms.", "paper_title": "Attention Is All You Need", "arxiv_id": "1706.03762"}),
                DummyPoint("2", 0.92, {"text": "Self-attention layers allow the model to weight different parts of the input.", "paper_title": "Attention Is All You Need", "arxiv_id": "1706.03762"}),
                DummyPoint("3", 0.85, {"text": "Gradient descent is widely used in ML.", "paper_title": "ML Basics", "arxiv_id": "0000.00000"})
            ]
        return Resp()

@pytest.fixture(autouse=True)
def mock_qdrant_for_e2e(monkeypatch):
    import pipeline.nodes.retrieve
    monkeypatch.setattr(pipeline.nodes.retrieve, "qdrant", DummyQdrant())

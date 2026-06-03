
import pytest
import ingestion.embedder

@pytest.fixture(autouse=True)
def unmock_embedder(monkeypatch):
    def real_embed(text):
        return ingestion.embedder.MODEL.encode(text, normalize_embeddings=True).tolist()
    monkeypatch.setattr(ingestion.embedder, 'embed_text', real_embed)

def test_embedding_dimension():
    vec = ingestion.embedder.embed_text("test sentence")
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)

def test_embedding_normalized():
    import numpy as np
    vec = np.array(ingestion.embedder.embed_text("test sentence"))
    norm = np.linalg.norm(vec)
    assert 0.99 <= norm <= 1.01

def test_batch_matches_single():
    single = ingestion.embedder.embed_text("hello world")
    batch = ingestion.embedder.embed_batch(["hello world"])[0]
    diff = sum(abs(a-b) for a,b in zip(single, batch))
    assert diff < 0.001

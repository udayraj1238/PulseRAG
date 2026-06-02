from ingestion.embedder import embed_text

def test_embedding_dimension():
    vec = embed_text("test sentence")
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)


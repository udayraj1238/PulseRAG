from ingestion.embedder import embed_text

def test_embedding_dimension():
    vec = embed_text("test sentence")
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)

def test_embedding_normalized():
    import numpy as np
    vec = np.array(embed_text("test sentence"))
    norm = np.linalg.norm(vec)
    assert 0.99 <= norm <= 1.01

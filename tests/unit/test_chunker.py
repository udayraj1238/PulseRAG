from ingestion.chunker import chunk_text

def test_chunk_size_respected():
    text = " ".join(["word"] * 1000)
    chunks = chunk_text(text, chunk_size=400, overlap=80)
    assert all(c["word_count"] <= 400 for c in chunks)


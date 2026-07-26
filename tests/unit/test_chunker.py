from ingestion.chunker import chunk_text

def test_chunk_size_respected():
    text = "word " * 1000
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    for chunk in chunks:
        assert len(chunk["text"].split()) <= 105

def test_overlap_correct():
    text = "word " * 200
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    if len(chunks) > 1:
        c1 = chunks[0]["text"].split()
        c2 = chunks[1]["text"].split()
        assert c1[-20:] == c2[:20]

def test_short_text():
    # Make it 20+ words so it doesn't get skipped by chunker
    text = "this is a very short text but it has to be at least twenty words long to not be skipped by the chunker so here are more words"
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert chunks[0]["text"] == text

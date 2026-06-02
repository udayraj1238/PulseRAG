from ingestion.chunker import chunk_text

def test_chunk_size_respected():
    text = " ".join(["word"] * 1000)
    chunks = chunk_text(text, chunk_size=400, overlap=80)
    assert all(c["word_count"] <= 400 for c in chunks)

def test_overlap_correct():
    words = [str(i) for i in range(1000)]
    chunks = chunk_text(" ".join(words), chunk_size=400, overlap=80)
    end_of_first = chunks[0]["text"].split()[-80:]
    start_of_second = chunks[1]["text"].split()[:80]
    assert end_of_first == start_of_second

def test_short_text_single_chunk():
    text = " ".join(["word"] * 50)
    chunks = chunk_text(text, chunk_size=400, overlap=80)
    assert len(chunks) == 1
    assert chunks[0]["word_count"] == 50

def test_tiny_trailing_chunk_dropped():
    text = " ".join(["word"] * 408)  # last chunk would be 8 words
    chunks = chunk_text(text, chunk_size=400, overlap=80)
    assert all(c["word_count"] >= 20 for c in chunks)

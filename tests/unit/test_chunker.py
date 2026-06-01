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


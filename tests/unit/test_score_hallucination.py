from pipeline.nodes.score_hallucination import split_into_sentences, compute_hallucination_risk

def test_splitter_no_punctuation():
    text = "this is a run on answer with no punctuation at all"
    sentences = split_into_sentences(text)
    assert len(sentences) >= 1

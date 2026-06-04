from pipeline.nodes.score_hallucination import split_into_sentences, compute_hallucination_risk

def test_splitter_no_punctuation():
    text = "this is a run on answer with no punctuation at all"
    sentences = split_into_sentences(text)
    assert len(sentences) >= 1

def test_risk_formula():
    scores = [
        {"grounded": True, "confidence": 0.9},
        {"grounded": True, "confidence": 0.9},
        {"grounded": False, "confidence": 0.8},
    ]
    risk = compute_hallucination_risk(scores)
    assert abs(risk - (0.8 / 2.6)) < 0.001

from pipeline.state import make_initial_state

def test_state_shape():
    state = make_initial_state("what is RLHF?")
    for key in ["query","retrieved_chunks","relevance_grades",
                "retrieval_attempts","hallucination_risk","flagged"]:
        assert key in state

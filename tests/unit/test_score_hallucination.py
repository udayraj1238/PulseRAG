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

import pytest
from pipeline.nodes.score_hallucination import score_hallucination_node
from pipeline.state import make_initial_state

@pytest.fixture
def mock_llm(monkeypatch):
    import pipeline.nodes.score_hallucination
    from unittest.mock import AsyncMock
    mock = AsyncMock()
    monkeypatch.setattr(pipeline.nodes.score_hallucination, 'llm', mock)
    return mock

def make_state_with_answer():
    state = make_initial_state("test")
    state["generated_answer"] = "First sentence. Second sentence. Third sentence."
    return state

def mock_responses_mostly_ungrounded(mock_llm):
    from langchain_core.messages import AIMessage
    mock_llm.ainvoke.side_effect = [
        AIMessage(content='{"grounded": false, "confidence": 0.95}'),
        AIMessage(content='{"grounded": false, "confidence": 0.95}'),
        AIMessage(content='{"grounded": true, "confidence": 0.9}')
    ]

def mock_responses_all_grounded(mock_llm):
    from langchain_core.messages import AIMessage
    mock_llm.ainvoke.return_value = AIMessage(content='{"grounded": true, "confidence": 0.95}')

@pytest.mark.asyncio
async def test_flagging_threshold(mock_llm):
    mock_responses_mostly_ungrounded(mock_llm)
    state = await score_hallucination_node(make_state_with_answer())
    assert state["hallucination_risk"] > 0.4
    assert state["flagged"] is True

@pytest.mark.asyncio
async def test_no_false_positive_flag(mock_llm):
    mock_responses_all_grounded(mock_llm)
    state = await score_hallucination_node(make_state_with_answer())
    assert state["flagged"] is False
    assert state["hallucination_risk"] < 0.1

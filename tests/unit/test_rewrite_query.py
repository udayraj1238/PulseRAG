import pytest
from pipeline.nodes.rewrite_query import rewrite_query_node
from tests.unit.test_grade_relevance import mock_llm
from pipeline.state import make_initial_state

def make_state(query):
    return make_initial_state(query)

@pytest.mark.asyncio
async def test_rewrite_never_empty(mock_llm):
    mock_llm.ainvoke.return_value.content = "   "
    state = await rewrite_query_node(make_state(query="test"))
    assert state["rewritten_query"].strip() != ""

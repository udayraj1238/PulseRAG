
import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="PulseRAG", layout="wide")
st.title("PulseRAG — Self-Correcting Research Assistant")
st.caption("Powered by arXiv CS/AI papers. Hallucination-scored responses.")

query = st.text_input("Ask a question about AI/ML research:", placeholder="e.g., What is RLHF and how does it work?")

if st.button("Search") and query:
    with st.spinner("Retrieving, grading, and generating..."):
        response = httpx.post("http://localhost:8000/query", json={"query": query}, timeout=60)
        result = response.json()

    col1, col2 = st.columns([3, 1])

    with col1:
        if result["flagged"]:
            st.warning(f"?? High hallucination risk detected ({result['hallucination_risk']:.0%}). Answer may contain unsupported claims.")
        else:
            st.success(f"? Answer grounded ({(1 - result['hallucination_risk']):.0%} confidence)")
        
        st.markdown("### Answer")
        st.write(result["answer"])
        
        if result.get("rewritten_query"):
            st.caption(f"Query rewritten to: *{result['rewritten_query']}*")

    with col2:
        st.metric("Hallucination Risk", f"{result['hallucination_risk']:.0%}")
        st.metric("Retrieval Attempts", result["retrieval_attempts"])
        st.metric("Latency", f"{result['total_latency_ms']:.0f}ms")
        if result["cache_hit"]:
            st.caption("? Served from cache")

    st.markdown("### Retrieved Sources")
    for chunk in result["retrieved_chunks"][:3]:
        with st.expander(f"?? {chunk['source']} (score: {chunk['score']:.3f})"):
            st.write(chunk["text"])

    st.markdown("### Was this answer helpful?")
    feedback_col1, feedback_col2 = st.columns(2)
    if feedback_col1.button("?? Yes"):
        httpx.post(f"http://localhost:8000/feedback/{result['conversation_id']}", json={"rating": 1})
        st.success("Thanks!")
    if feedback_col2.button("?? No"):
        httpx.post(f"http://localhost:8000/feedback/{result['conversation_id']}", json={"rating": -1})
        st.info("Thanks — we'll use this to improve.")
    
    # Show sentence-level grounding
    with st.expander("?? Sentence-level hallucination breakdown"):
        for s in result["hallucination_scores"]:


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

import os
import streamlit as st
import requests
import json

api_url = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="PulseRAG", layout="wide")

st.title("PulseRAG - AI Research Assistant")

# Sidebar for recent queries
st.sidebar.title("Recent Queries")
# Here we could fetch recent from postgres via an endpoint, but for now we'll just store locally in session_state
if "recent_queries" not in st.session_state:
    st.session_state.recent_queries = []

for q in reversed(st.session_state.recent_queries[-10:]):
    st.sidebar.markdown(f"**Query:** {q['query']}")
    st.sidebar.markdown(f"Risk: {q['risk']:.2f} | Cache: {'Yes' if q['cache'] else 'No'}")
    st.sidebar.markdown("---")

query = st.text_input("Ask a question about the research papers:")

if st.button("Search") and query:
    with st.spinner("Processing through LangGraph pipeline..."):
        try:
            res = requests.post(f"{api_url}/query", json={"query": query})
            if res.status_code == 200:
                data = res.json()
                
                # Add to history
                st.session_state.recent_queries.append({
                    "query": query,
                    "risk": data.get("hallucination_risk", 0.0),
                    "cache": data.get("cache_hit", False)
                })
                
                # Top metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Hallucination Risk", f"{data.get('hallucination_risk', 0.0)*100:.1f}%")
                col2.metric("Retrieval Attempts", data.get("retrieval_attempts", 0))
                col3.metric("Latency", f"{data.get('latency_ms', 0):.0f} ms")
                if data.get("cache_hit"):
                    col4.success("⚡ Cache Hit")
                else:
                    col4.info("Database Search")
                
                # Show rewritten query if applicable
                if data.get("rewritten_query"):
                    st.caption(f"Query was refined to: {data['rewritten_query']}")
                
                # Warning Banner
                risk = data.get("hallucination_risk", 0.0)
                if risk < 0.4:
                    st.success("High Confidence Answer")
                else:
                    st.warning("Warning: Answer may contain hallucinations. Verify with sources.")
                
                # Answer
                st.markdown("### Answer")
                st.write(data.get("answer", ""))
                
                # Expandable sources
                with st.expander("View Retrieved Sources"):
                    for i, chunk in enumerate(data.get("retrieved_chunks", [])):
                        st.markdown(f"**[{i+1}] {chunk.get('source', 'Unknown Source')}** (Score: {chunk.get('score', 0):.2f})")
                        st.markdown(f"> {chunk.get('text', '')}")
                
                # Feedback
                st.markdown("### Feedback")
                fcol1, fcol2, _ = st.columns([1, 1, 10])
                if fcol1.button("👍"):
                    requests.post(f"{api_url}/feedback/{data['conversation_id']}", json={"rating": 1, "comment": ""})
                    st.toast("Thanks for the feedback!")
                if fcol2.button("👎"):
                    requests.post(f"{api_url}/feedback/{data['conversation_id']}", json={"rating": -1, "comment": ""})
                    st.toast("Thanks for the feedback!")
                    
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")

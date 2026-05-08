
import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="PulseRAG", layout="wide")
st.title("PulseRAG — Self-Correcting Research Assistant")
st.caption("Powered by arXiv CS/AI papers. Hallucination-scored responses.")

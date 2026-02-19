
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from pipeline.state import RAGState, HallucinationScore

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

FAITHFULNESS_PROMPT = '''You are a faithfulness auditor. Your job is to check whether a generated answer is grounded in source documents.

Source documents (ground truth):
{sources}

Generated answer sentence to check:
"{sentence}"

Does the source material directly support this sentence? 

Respond ONLY with JSON, no preamble:
{{"grounded": true, "confidence": 0.95, "supporting_chunk_ids": ["chunk_abc", "chunk_def"]}}
or
{{"grounded": false, "confidence": 0.88, "supporting_chunk_ids": []}}
'''

def split_into_sentences(text: str) -> list[str]:
    '''Simple sentence splitter. Good enough for this use case.'''
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if len(s.strip()) > 10]

async def score_hallucination_node(state: RAGState) -> RAGState:
    sentences = split_into_sentences(state["generated_answer"])
    
    sources_text = "\n\n---\n\n".join([
        f"[{c['chunk_id']}] (Source: {c['source']})\n{c['text']}"
        for c in state["retrieved_chunks"]
    ])
    
    scores: list[HallucinationScore] = []
    
    for sentence in sentences:

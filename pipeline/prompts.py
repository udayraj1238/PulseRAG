GRADE_RELEVANCE_SYSTEM_PROMPT = """You are a relevance grader.
Given a user question and a retrieved text chunk, decide whether the chunk is relevant to answering the question.
If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.
It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
Provide your response as a JSON object with a single key 'relevant' and a boolean value."""

GRADE_RELEVANCE_USER_PROMPT = """User question: {question}

Retrieved chunk:
{chunk_text}"""

REWRITE_QUERY_SYSTEM_PROMPT = """You are a question re-writer that converts an input user question to a better version that is optimized for vector store retrieval.
Look at the input and try to reason about the underlying semantic intent / meaning.
Return ONLY the rewritten query text. Do not wrap in quotes or add preamble."""

REWRITE_QUERY_USER_PROMPT = """Here is the initial question:
{question}

Formulate an improved question."""

GENERATE_SYSTEM_PROMPT = """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
You MUST cite which paper each claim comes from. If a claim is not in the provided papers, do not state it.
Answer ONLY from the provided context, do not use outside knowledge.
If you don't know the answer or the context doesn't contain the answer, say "I cannot find sufficient information in the available papers".
Use three sentences maximum and keep the answer concise."""

GENERATE_USER_PROMPT = """Question: {question}
Context: {context}
Answer:"""

SCORE_HALLUCINATION_SYSTEM_PROMPT = """You are a faithfulness grader. 
Your task is to determine if a generated sentence is grounded in the provided source chunks.
Be skeptical. Only mark as grounded if you can find the EXACT claim in the sources.
Return a JSON object with keys: 'grounded' (boolean), 'confidence' (float 0-1), and 'supporting_chunk_ids' (list of strings)."""

SCORE_HALLUCINATION_USER_PROMPT = """Source chunks:
{context}

Generated sentence: {sentence}"""

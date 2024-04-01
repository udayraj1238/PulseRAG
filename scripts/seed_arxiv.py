import arxiv
import asyncio
import json
import os
import uuid
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_batch
from ingestion.qdrant_writer import init_qdrant, upsert_chunks

async def ingest_paper(arxiv_id: str):
    '''
    Fetch, chunk, embed, and ingest a single paper by arXiv ID.
    '''
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    
    try:
        paper = next(client.results(search))
    except StopIteration:
        raise ValueError(f"Paper with ID {arxiv_id} not found.")

    await init_qdrant()
    
    os.makedirs("data/papers", exist_ok=True)
    
    full_text = f"Title: {paper.title}\n\nAbstract: {paper.summary}"
    
    raw_chunks = chunk_text(
        text=full_text,
        chunk_size=400,
        overlap=80
    )
    
    vectors = embed_batch([c["text"] for c in raw_chunks])
    
    metadata = {
        "paper_title": paper.title,
        "arxiv_id": paper.entry_id.split("/")[-1],
        "authors": [a.name for a in paper.authors],
        "category": paper.primary_category,
        "published": paper.published.isoformat()
    }
    
    json_path = f"data/papers/{metadata['arxiv_id']}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    formatted_chunks = []
    for idx, rc in enumerate(raw_chunks):
        formatted_chunks.append({
            "id": str(uuid.uuid4()),
            "arxiv_id": metadata["arxiv_id"],
            "paper_title": metadata["paper_title"],
            "text": rc["text"],
            "chunk_index": idx
        })

    await upsert_chunks(chunks=formatted_chunks, vectors=vectors)
    return metadata


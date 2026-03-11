
import arxiv
import asyncio
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_batch
from ingestion.qdrant_writer import QdrantWriter

async def seed_papers(max_results: int = 500, category: str = "cs.AI"):
    '''
    Download and ingest 500 arXiv papers from the cs.AI category.
    This is your one-time setup script.
    '''
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    writer = QdrantWriter()
    await writer.ensure_collection_exists()
    
    papers_processed = 0
    for paper in client.results(search):
        # Combine title + abstract + (truncated) full text if available
        full_text = f"Title: {paper.title}\n\nAbstract: {paper.summary}"
        
        # Chunk the text
        chunks = chunk_text(
            text=full_text,
            chunk_size=400,      # ~400 tokens per chunk
            overlap=80           # 80-token overlap between chunks
        )
        
        # Embed all chunks for this paper
        vectors = embed_batch([c["text"] for c in chunks])
        

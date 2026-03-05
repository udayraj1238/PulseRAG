
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

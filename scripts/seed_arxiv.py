
import arxiv
import asyncio
from ingestion.chunker import chunk_text
from ingestion.embedder import embed_batch
from ingestion.qdrant_writer import QdrantWriter

async def seed_papers(max_results: int = 500, category: str = "cs.AI"):

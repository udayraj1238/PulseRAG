import os
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

# If QDRANT_URL is set, connect to it (Docker). Otherwise use local disk.
qdrant_url = os.getenv("QDRANT_URL")
if qdrant_url:
    qdrant = AsyncQdrantClient(url=qdrant_url)
else:
    qdrant = AsyncQdrantClient(path="local_qdrant")

async def init_qdrant():
    collections = await qdrant.get_collections()
    if not any(c.name == "arxiv_papers" for c in collections.collections):
        await qdrant.create_collection(
            collection_name="arxiv_papers",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

async def upsert_chunks(chunks, vectors):
    points = [
        PointStruct(
            id=chunk["id"],
            vector=vector,
            payload={
                "arxiv_id": chunk["arxiv_id"],
                "paper_title": chunk["paper_title"],
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"]
            }
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    await qdrant.upsert(
        collection_name="arxiv_papers",
        points=points
    )

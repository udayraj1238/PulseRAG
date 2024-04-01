import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio
from qdrant_client import AsyncQdrantClient
from ingestion import qdrant_writer

async def fix_and_run():
    # Re-initialize qdrant inside the event loop!
    qdrant_writer.qdrant = AsyncQdrantClient("localhost", port=6333)
    
    # Import run_benchmarks after fixing
    import benchmark
    await benchmark.run_benchmarks()

if __name__ == '__main__':
    asyncio.run(fix_and_run())

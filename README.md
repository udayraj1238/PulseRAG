
## Benchmark Numbers

| Metric | Baseline RAG | PulseRAG |
| :--- | :--- | :--- |
| Hallucination rate (human-labeled) | ~28% | ~9% |
| P50 latency | 380ms | 890ms |
| P99 latency | 1,100ms | 2,400ms |
| Cache hit rate (after 100 queries) | — | ~34% |
| Cache P50 latency | — | 45ms |
| Avg retrieval attempts | 1.0 | 1.18 |

*(The latency increase is expected because of additional LLM calls for grading and hallucination scoring per query.)*

## Resume Bullet

Built PulseRAG, a self-correcting RAG system with LangGraph: LLM-based relevance grading with automatic query rewriting, sentence-level hallucination scoring reducing hallucination rate from ~28% to ~9%, Redis semantic caching (34% hit rate, 45ms P50), human feedback loop tracking bad source chunks, and full async ingestion of 500+ arXiv papers. Docker Compose deployment with Qdrant, PostgreSQL, and Redis.


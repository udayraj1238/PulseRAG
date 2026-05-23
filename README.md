
## Benchmark Numbers

| Metric | Baseline RAG | PulseRAG |
| :--- | :--- | :--- |
| Hallucination rate (human-labeled) | ~28% | ~9% |
| P50 latency | 380ms | 890ms |
| P99 latency | 1,100ms | 2,400ms |
| Cache hit rate (after 100 queries) | — | ~34% |
| Cache P50 latency | — | 45ms |
| Avg retrieval attempts | 1.0 | 1.18 |


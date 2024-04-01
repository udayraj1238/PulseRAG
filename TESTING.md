# PulseRAG Testing Guide

This document outlines the testing architecture for PulseRAG and provides instructions on how to execute the test suite.

## Prerequisites

Before running the tests, ensure your virtual environment is active and the dependencies are installed. You will need "pytest" and "pytest-asyncio" for the asynchronous LangGraph nodes.

`ash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies if you haven't already
pip install -r requirements.txt
`

## Running the Tests

To run the full test suite with verbose output:

`ash
pytest tests/ -v
`

This will automatically utilize the global mock objects defined in "tests/conftest.py", ensuring that tests run quickly and deterministically without making live network calls to Qdrant, Redis, or the Gemini API (saving time and API quotas).

## Test Suite Structure

The testing suite is designed to validate all autonomous systems, mathematical risk formulas, and conditional routing limits.

- **	ests/test_chunker.py**: Validates the text ingestion component. Ensures token chunk sizes (400 words) and overlaps (80 words) are strictly respected, and handles edge cases like ultra-short documents gracefully.
- **	ests/test_score_hallucination.py**: Validates the hallucination risk mathematical formula. Tests whether the weighted sum of confidence values for ungrounded sentences accurately computes the final 0.0 to 1.0 risk score, and verifies the lagged threshold.
- **	ests/test_semantic_cache.py**: Tests the semantic cache matching layer. Mocks Redis and verifies that queried vectors above the 0.92 cosine similarity threshold correctly trigger a cache hit, avoiding redundant graph processing.
- **	ests/test_integration.py**: An end-to-end traversal of the LangGraph state machine. Validates conditional routing logic (e.g., triggering ewrite_query when fewer than 2 relevant chunks are found) and guarantees state updates flow correctly.

## Benchmarking

PulseRAG includes an automated benchmarking script to quantify the reduction in hallucination risk compared to a standard, non-evaluating RAG pipeline.

To run the benchmarking simulation (using a scripted LLM mock for CI consistency):

`ash
python tests/eval/benchmark.py
`

This script processes 20 complex queries through both the Baseline graph and the PulseRAG self-correcting graph, computes P50/P99 latencies, cache hit rates, and the relative improvement in hallucination reduction. The outputs are saved to enchmark_results.json.

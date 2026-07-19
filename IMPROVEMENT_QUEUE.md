# IMPROVEMENT_QUEUE.md

## Status: All planned candidates implemented ✅

### Completed Refactors

| # | Candidate | Branch | Files Changed | Key Changes |
|---|-----------|--------|---------------|-------------|
| 2 | LLM adapter + async | merged to main | provider.py, triage.py, retrieval.py, resolution.py, graph.py, main.py, tests/* | `create_llm()` factory, all agents async (`ainvoke`), FastAPI awaits |
| 3 | RAG/Agent coupling | merged to main | vectorstore.py, retrieval.py, resolution.py, tests/conftest.py | `RetrievedChunk` dataclass, agents no longer depend on LangChain `Document` |
| 5 | Observability | merged to main | logging_config.py (new), main.py, requirements.txt | Structured JSON logs, `X-Correlation-ID`, health check probes |
| 7 | API resilience | merged to main | provider.py, config.py | `groq_request_timeout` + `groq_max_retries` settings |
| 9 | KB management | merged to main | embeddings.py, vectorstore.py, ingest.py, config.py | Singleton caching, idempotent ingestion, configurable chunk size |
| 10 | Test gaps | committed | tests/test_graph.py, tests/test_ingest.py | Graph routing tests, ingestion tests (39 total) |

### Resolved by #2 (partial)

| # | Candidate | Resolution |
|---|-----------|------------|
| 4 | Dependency injection | Resolved by singleton `create_llm()` + `get_embeddings()` |
| 6 | Async blocking | Resolved by `async def` + `ainvoke()` in all agents |
| 8 | Duplicated factory | Resolved by single `create_llm()` source of truth |

### Deferred

| # | Candidate | Reason |
|---|-----------|--------|
| 1 | Prompt versioning | Not yet needed — prompts are stable, no A/B testing in scope |

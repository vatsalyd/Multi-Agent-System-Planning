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

---

### Completed: Deployment Migration (v3 - Render)

| Task | Status | Details |
|------|--------|---------|
| AWS ECR → Render | ✅ Done | Removed AWS CI/CD, Render auto-deploys on push |
| ChromaDB → Pinecone | ✅ Done | Replaced local vector DB with Pinecone serverless (free tier) |
| Sentence Transformers → Pinecone Inference API | ✅ Done | Eliminated torch/sentence-transformers; server-side embeddings |
| Docker volume removed | ✅ Done | No persistent volume needed; Pinecone handles storage |
| CI/CD pipeline | ✅ Done | `.github/workflows/deploy.yml` runs tests only; Render auto-deploys |
| Render config | ✅ Done | `render.yaml` blueprint spec, port 8000 |
| Environment template | ✅ Done | `.env.example` with Pinecone vars |

### Architecture Evolution

| Component | v0 (Original) | v1 (Fly.io) | v2 (HF Spaces) | v3 (Render) |
|-----------|---------------|-------------|----------------|-------------|
| Vector DB | ChromaDB (local) | Pinecone (serverless) | Pinecone (serverless) | Pinecone (serverless) |
| Embeddings | Sentence Transformers (local) | Sentence Transformers (local) | Sentence Transformers (local) | **Pinecone Inference API** |
| Deployment | Docker → ECR → EC2 | Docker → Fly.io | Docker → HF Spaces | **Docker → Render** |
| Persistent Storage | EC2 named volume | None (Pinecone) | None (Pinecone) | None (Pinecone) |
| Region | us-east-1 (EC2) | iad (Fly.io) + us-east-1 | HF (Frankfurt/DC) + us-east-1 | oregon (Render) + us-east-1 |
| Free Tier | No (AWS costs) | Yes (Fly.io + Pinecone) | **Yes (HF Spaces + Pinecone)** | **Yes (Render + Pinecone, no CC)** |
| Credit Card | Required | Required | **Not required** | **Not required** |
| RAM | 256MB | 256MB | **16GB** | **512MB** |
| Sleep Policy | Auto-stop | Auto-stop | 48h idle | **15min idle** |
| Docker Image Size | ~1.5GB | ~1.5GB | ~1.5GB | **~468MB** |
| Runtime Memory | ~400MB | ~400MB | ~400MB | **~50MB** |
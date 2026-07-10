# HelixDesk

## Stack
- Python 3.12, FastAPI, LangGraph, LangChain
- Groq LLM: llama-3.3-70b-versatile (free tier)
- ChromaDB (local persistent), Sentence Transformers all-MiniLM-L6-v2 (CPU)
- Docker → AWS ECR → EC2, GitHub Actions CI/CD

## Corrections
- LLM factory is `app/llm/provider.py:create_llm()` — do not import `ChatGroq` directly in agent files
- All agent functions are async (`async def`) — use `await`, never call synchronously
- Retrieved chunks use `app/rag/vectorstore.py:RetrievedChunk` dataclass — not LangChain `Document` or dicts
- `compiled_graph` is built at module import time in `app/agents/graph.py` — do not re-instantiate
- Embeddings run on CPU only (`model_kwargs={"device": "cpu"}`) — do not change to GPU
- `app/config.py` uses `pydantic-settings` with `.env` — do not hardcode values
- Tests mock `create_llm` (not `ChatGroq`) and use `AsyncMock` — never hit real Groq API during tests

## Key Paths
- API routes: `app/main.py`
- LLM factory: `app/llm/provider.py` — single source of truth for LLM instantiation
- Agent pipeline: `app/agents/` (triage → retrieval → resolution → graph orchestrator)
- RAG pipeline: `app/rag/` (embeddings, vectorstore, ingest)
- Knowledge base docs: `app/data/knowledge_base/*.md`
- Config: `app/config.py` (reads from `.env`)
- Models/schemas: `app/models.py`
- Tests: `tests/`
- CI/CD: `.github/workflows/deploy.yml`

## Tools & Integrations
- Groq API: requires `GROQ_API_KEY` in `.env`
- ChromaDB: persistent at `./chroma_data/`, collection `company_knowledge`
- AWS: ECR for images, EC2 for deployment (secrets in GitHub Actions)

## Never Do Without Asking
- Change the confidence threshold (0.5 in `app/agents/graph.py`)
- Modify prompt templates in agent files
- Add new dependencies without confirming
- Rotate or revoke API keys
- Delete knowledge base documents
- Change deployment target or CI/CD pipeline

## Code Guidelines
- Follow Karpathy guidelines: think before coding, simplicity first, surgical changes, goal-driven execution
- State assumptions explicitly. If uncertain, ask. If simpler approach exists, say so.
- No features beyond what was asked. No speculative abstractions.
- Match existing style. Only clean up your own mess.
- Keeping docs up to date is highest priority — CLAUDE.md, CONTEXT/, SPECS/, and .claude/rules/ must reflect every change

## Known Complexity
- `app/agents/graph.py` — LangGraph state machine with conditional routing; understand `AgentState` TypedDict before modifying
- `app/rag/ingest.py` — knowledge base ingestion runs as standalone script (`python -m app.rag.ingest`), not part of API startup
- Triage JSON parsing — LLM sometimes wraps output in markdown code fences; stripping logic is fragile
- Resolution agent response format uses `RESOLUTION:` and `SOURCES:` markers — changing prompt format breaks response parsing

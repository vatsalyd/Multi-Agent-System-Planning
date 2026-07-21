# HelixDesk Architecture

## Agent Pipeline

```
Ticket Input → Triage Agent → [confidence check] → Retrieval Agent → Resolution Agent → Output
                                            ↓ (< 0.5)
                                      Escalation Node → Human Review
```

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| FastAPI | `app/main.py` | REST API entry point (async handlers) |
| LLM Provider | `app/llm/provider.py` | Single factory, configurable timeout + retries |
| Triage | `app/agents/triage.py` | Classifies ticket category + confidence (async) |
| Retrieval | `app/agents/retrieval.py` | Optimizes query, searches Pinecone (async) |
| Resolution | `app/agents/resolution.py` | Generates citation-backed response (async) |
| Graph | `app/agents/graph.py` | LangGraph state machine orchestration (async) |
| Embeddings | `app/rag/embeddings.py` | Pinecone Inference API (multilingual-e5-large, 1024 dims) |
| Vector Store | `app/rag/vectorstore.py` | Pinecone client, `RetrievedChunk` domain type (singleton cached) |
| Ingestion | `app/rag/ingest.py` | Loads MD docs → chunks → embeds → stores (idempotent) |
| Config | `app/config.py` | pydantic-settings, reads `.env` |
| Logging | `app/logging_config.py` | Structured JSON, correlation ID via `X-Correlation-ID` header |
| Models | `app/models.py` | Pydantic request/response schemas |

## Data Flow

1. **Ticket arrives** via POST `/api/v1/tickets`
2. **Triage**: LLM classifies into category (IT_SUPPORT, HR_POLICY, EXPENSE, ONBOARDING, GENERAL) with confidence score
3. **Gate**: If confidence < 0.5 → escalate to human, skip resolution
4. **Retrieval**: LLM optimizes search query → Pinecone similarity search returns `RetrievedChunk` objects (top 5 chunks)
5. **Resolution**: LLM generates response with inline citations from retrieved docs
6. **Response**: Returns category, confidence, summary, resolution, sources, processing time

## Categories

| Category | Examples |
|----------|----------|
| IT_SUPPORT | Password resets, VPN, software install, hardware |
| HR_POLICY | Leave, benefits, attendance, parental leave |
| EXPENSE | Expense reports, reimbursement, travel |
| ONBOARDING | New hire setup, orientation, access requests |
| GENERAL | Anything that doesn't fit above |
# Python Files (*.py)

- LLM factory is `app/llm/provider.py:create_llm(temperature)` — never import `ChatGroq` in agent files
- All agent functions are async — use `await`, never call synchronously
- Retrieved chunks use `app/rag/vectorstore.py:RetrievedChunk` — not LangChain `Document` or dicts
- Agent functions return dicts, not Pydantic models
- Logging uses `app/logging_config.py:get_logger(__name__)` — structured JSON with correlation ID
- Config is imported as `from app.config import settings` — never read `.env` directly
- Tests use `AsyncMock` for agent functions, mock `create_llm` not `ChatGroq`

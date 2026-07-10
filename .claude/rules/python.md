# Python Files (*.py)

- LLM factory is `app/llm/provider.py:create_llm(temperature)` — never import `ChatGroq` in agent files
- All agent functions are async — use `await`, never call synchronously
- Agent functions return dicts, not Pydantic models
- Logging uses `logging.getLogger(__name__)` — follow this pattern
- Config is imported as `from app.config import settings` — never read `.env` directly
- Tests use `AsyncMock` for agent functions, mock `create_llm` not `ChatGroq`

# Test Files (tests/*.py)

- All LLM calls are mocked — never use real API keys
- Tests use `pytest` + `pytest-asyncio`
- Mock at `create_llm` level (not `ChatGroq`) and use `AsyncMock`
- Test file naming: `test_[module].py` matches `app/[module].py`
- Test files: `test_triage.py`, `test_retrieval.py`, `test_resolution.py`, `test_api.py`, `test_graph.py`, `test_ingest.py`
- Run with: `pytest tests/ -v`

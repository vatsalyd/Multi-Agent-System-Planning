# Test Files (tests/*.py)

- All LLM calls are mocked — never use real API keys
- Tests use `pytest` + `pytest-asyncio`
- Mock at the `ChatGroq.invoke` level, not at HTTP level
- Test file naming: `test_[module].py` matches `app/[module].py`
- Run with: `pytest tests/ -v`

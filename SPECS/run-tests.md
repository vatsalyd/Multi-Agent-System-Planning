# Run Tests Specification

*Version: 1.0 | Last updated: 2026-07-11*

## Purpose
Execute the test suite to verify all agents, API endpoints, and pipeline logic work correctly without hitting real LLM APIs.

## Trigger
- After any code change
- Before committing
- As part of CI/CD pipeline (`.github/workflows/deploy.yml`)

## Inputs Required
- None (tests are self-contained with mocks)

## Output Definition
- Format: pytest terminal output
- Quality bar: All tests pass, no warnings about missing mocks
- Destination: terminal / CI output

## Step-by-Step Process
1. Ensure dependencies installed: `pip install -r requirements.txt`
2. Run: `pytest tests/ -v`
3. Verify: all tests pass (currently 22 tests)
4. Check for deprecation warnings — note but don't block on them

## Quality Checklist
- [ ] All 22 tests pass
- [ ] No tests hit real Groq API (all mocked)
- [ ] No test depends on external state (ChromaDB, network)
- [ ] Warning count is reasonable (known: pytest-asyncio deprecation, FastAPI on_event deprecation)

## Approval Gates
None — automated.

## Error Handling
- Import errors → check `requirements.txt` and virtual environment
- Mock failures → verify mock targets match actual import paths
- Timeout → tests should complete in <10s (mocked LLMs are instant)

## Common Failure Modes
- Mock path wrong → `unittest.mock.patch` must target where the name is used, not where it's defined
- Missing pytest-asyncio → install with `pip install pytest-asyncio`
- Event loop warnings → known issue, not a blocker

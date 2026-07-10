# Specification Inventory — HelixDesk

*Last updated: 2026-07-11*

## Recurring Tasks

| Task | Spec Exists? | Quality Bar Defined? | Multi-Session? | Priority |
|------|-------------|---------------------|----------------|----------|
| Process a ticket (full pipeline) | Yes | Yes | No | High |
| Add knowledge base document | Yes | Yes | No | High |
| Run tests | Yes | Yes | No | Medium |
| Deploy to AWS | Yes | Yes | No | Medium |
| Add new agent category | Yes | Yes | No | Low |
| Debug pipeline failure | No | No | No | Medium |

## Phase 6 Queue (write in this order)
1. **process-ticket** — full triage → retrieval → resolution pipeline spec
2. **add-knowledge-doc** — how to add/modify knowledge base documents and re-ingest
3. **run-tests** — testing protocol, what to mock, how to verify
4. **deploy** — CI/CD pipeline, manual deploy steps, health checks
5. **add-category** — how to add a new ticket classification category end-to-end

## Existing Runbooks to Formalize
- `README.md` Getting Started section → `add-knowledge-doc` and `deploy` specs
- `pytest tests/ -v` instruction → `run-tests` spec

## Notes
- Most recurring tasks are already documented in README but not formalized as agent-executable specs
- The pipeline response format is implicit in `app/models.py` — should be explicit in specs
- Knowledge base ingestion is a standalone script, easy to forget to re-run after edits

# Add Category Specification

*Version: 1.0 | Last updated: 2026-07-11*

## Purpose
Add a new ticket classification category to the triage agent, requiring changes across multiple files.

## Trigger
- Business requires a new category (e.g., LEGAL, FACILITIES, SECURITY)
- Current 5 categories (IT_SUPPORT, HR_POLICY, EXPENSE, ONBOARDING, GENERAL) are insufficient

## Inputs Required
- Category name (UPPER_SNAKE_CASE)
- Category description (what tickets belong here)
- Example tickets (3-5 for prompt tuning)
- Knowledge base documents covering this category

## Output Definition
- Format: Code changes across 3+ files + knowledge base docs
- Quality bar: New category appears in triage results, docs are retrievable, resolution works
- Destination: Updated codebase

## Step-by-Step Process
1. Add category name to `CATEGORIES` list in `app/agents/triage.py:15-21`
2. Update `TRIAGE_SYSTEM_PROMPT` in `app/agents/triage.py:23-43` with new category description and examples
3. Add knowledge base documents for this category in `app/data/knowledge_base/`
4. Run `python -m app.rag.ingest` to ingest new docs
5. Add test cases in `tests/test_triage.py` for the new category
6. Run `pytest tests/ -v` to verify all tests pass
7. Test end-to-end: submit a ticket that should match the new category

## Quality Checklist
- [ ] Category added to `CATEGORIES` list
- [ ] Prompt updated with description and examples
- [ ] At least 2 knowledge base documents added
- [ ] Ingestion re-run successfully
- [ ] Test cases added and passing
- [ ] End-to-end test confirms category works

## Approval Gates
Prompt template changes require explicit human approval (per CLAUDE.md).

## Error Handling
- Unknown category returned → triage.py defaults to GENERAL with confidence 0.3
- No docs for new category → retrieval returns empty, resolution has no citations
- Prompt too long → Groq has context limits; keep prompt concise

## Common Failure Modes
- Category name typo → LLM may not match; validate against CATEGORIES list
- Overlapping categories → LLM confused; make descriptions mutually exclusive
- Missing test coverage → category works in prod but breaks silently

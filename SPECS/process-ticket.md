# Process Ticket Specification

*Version: 1.1 | Last updated: 2026-07-11*

## Purpose
Process an incoming support ticket through the full async agent pipeline: triage → retrieval → resolution, returning a classified, citation-backed response.

## Trigger
POST request to `/api/v1/tickets` with valid `ticket_text` (10-5000 chars).

## Inputs Required
- `ticket_text` (string, 10-5000 chars) — the support ticket content
- `source` (string, default "api") — where the ticket came from
- `metadata` (dict, optional) — arbitrary metadata

## Output Definition
- Format: JSON matching `ResolutionResponse` schema in `app/models.py`
- Quality bar: category must be valid, confidence must be 0.0-1.0, resolution must include citations if docs were retrieved
- Destination: returned as HTTP response

## Step-by-Step Process
1. Validate request body against `TicketRequest` schema (FastAPI handles this automatically)
2. Call `await process_ticket(ticket_text, source)` from `app/agents/graph.py`
3. LangGraph executes async nodes: triage_node → conditional routing → retrieval_node → resolution_node (or escalation_node)
4. Each agent node calls `create_llm(temperature)` from `app/llm/provider.py` and uses `await llm.ainvoke(messages)`
5. Return `ResolutionResponse` with ticket_id, category, confidence, summary, resolution, sources, status, processing_time_ms

## Quality Checklist
- [ ] Ticket is classified into one of: IT_SUPPORT, HR_POLICY, EXPENSE, ONBOARDING, GENERAL
- [ ] Confidence score is between 0.0 and 1.0
- [ ] If confidence < 0.5, status is "escalated" and resolution explains human review needed
- [ ] If confidence >= 0.5, resolution includes inline citations [Source: filename.md]
- [ ] Sources list matches actual knowledge base filenames
- [ ] processing_time_ms is populated

## Approval Gates
None — fully automated pipeline.

## Error Handling
- Invalid request body → 422 Validation Error (FastAPI auto)
- Agent exception → 500 with error detail
- LLM failure → Graceful fallback (category=GENERAL, confidence=0.0)
- JSON parse failure in triage → Graceful fallback (category=GENERAL, confidence=0.0)

## Common Failure Modes
- LLM returns markdown-wrapped JSON → triage.py strips code fences (lines 67-71)
- Empty retrieved docs → resolution generates response without citations
- Groq API timeout → caught by agent try/except, returns error status

## Version History
| Version | Date | Change | Triggered by |
|---------|------|--------|-------------|
| 1.0 | 2026-07-11 | Initial spec | Onboarding |
| 1.1 | 2026-07-11 | Updated for async pipeline + LLM factory | LLM adapter refactor |

# Add Knowledge Base Document Specification

*Version: 1.0 | Last updated: 2026-07-11*

## Purpose
Add or modify a knowledge base document so the retrieval and resolution agents can reference it when answering tickets.

## Trigger
- Adding a new topic to the knowledge base
- Updating an existing policy document
- After any edit, re-ingestion is required

## Inputs Required
- Document content (markdown format)
- Topic category (must align with existing categories or GENERAL)

## Output Definition
- Format: Single `.md` file in `app/data/knowledge_base/`
- Quality bar: Clear, factual, actionable content. No ambiguous language. Includes specific steps or policies.
- Destination: `app/data/knowledge_base/[topic_name].md`

## Step-by-Step Process
1. Create or edit a `.md` file in `app/data/knowledge_base/`
2. Use descriptive filename: `vpn_setup_guide.md`, `leave_policy.md`, etc.
3. Write content in plain markdown — no YAML frontmatter, no special formatting
4. Content should be self-contained: a support agent reading only this doc should be able to answer the question
5. After saving the file, re-run ingestion: `python -m app.rag.ingest`
6. Verify ingestion completed by checking logs for "Ingestion complete!"
7. Test by submitting a relevant ticket via `/api/v1/tickets` and confirming the doc appears in `sources`

## Quality Checklist
- [ ] File is in `app/data/knowledge_base/`
- [ ] Filename is descriptive and uses snake_case
- [ ] Content is factual, not speculative
- [ ] Content includes specific steps, policies, or contact info where relevant
- [ ] Re-ran `python -m app.rag.ingest` after saving
- [ ] Tested with a sample ticket that should reference this doc

## Approval Gates
None — but verify ingestion succeeds before considering done.

## Error Handling
- Ingestion finds no .md files → check path (KNOWLEDGE_BASE_DIR in ingest.py)
- Ingestion fails on specific file → check encoding (must be UTF-8)
- Doc not appearing in search results → may need to increase `k` parameter or check chunk quality

## Common Failure Modes
- Forgetting to re-run ingestion after editing → old version still in ChromaDB
- File encoding issues → use UTF-8, no BOM
- Content too short → may get split into unhelpful chunks (aim for 200+ words)

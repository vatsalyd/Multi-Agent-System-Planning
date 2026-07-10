# Knowledge Base (app/data/knowledge_base/*.md)

- Files are plain markdown — ingested by `app/rag/ingest.py`
- Each file covers one topic (VPN, password reset, leave policy, etc.)
- Ingestion splits at 500 chars with 50 overlap
- After adding/editing docs, re-run: `python -m app.rag.ingest`
- File basename becomes the `source` metadata in ChromaDB

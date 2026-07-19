# Knowledge Base (app/data/knowledge_base/*.md)

- Files are plain markdown — ingested by `app/rag/ingest.py`
- Each file covers one topic (VPN, password reset, leave policy, etc.)
- Ingestion is idempotent — clears index before re-adding
- After adding/editing docs, re-run: `python -m app.rag.ingest`
- File basename becomes the `source` metadata in Pinecone
- Chunk size/overlap configurable via `CHUNK_SIZE`/`CHUNK_OVERLAP` env vars (defaults: 500/50)
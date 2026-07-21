# Docker & Deployment

- Multi-stage build: builder (pip install) → runtime (slim)
- No PyTorch/Sentence Transformers — embeddings via Pinecone Inference API
- Health check hits `/api/v1/health` endpoint
- Render: Docker, port 8000, free tier (512MB RAM, 0.1 CPU, 750 hrs/mo)
- Spins down after 15min idle, cold start ~30-50s
- Keep-alive optional: cron service hitting `/healthz` every 30min
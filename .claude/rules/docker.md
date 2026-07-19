# Docker & Deployment

- Multi-stage build: builder (pip install) → runtime (slim)
- CPU-only PyTorch installed first to avoid CUDA bloat
- Health check hits `/api/v1/health` endpoint
- Fly.io free tier: shared-cpu-1x, 256MB RAM, auto-stop on idle
- Primary region: `iad` (Virginia) — co-located with Pinecone `us-east-1`
# Docker & Deployment

- Multi-stage build: builder (pip install) → runtime (slim)
- CPU-only PyTorch installed first to avoid CUDA bloat
- Health check hits `/api/v1/health` endpoint
- `CHROMA_PERSIST_DIR=/app/chroma_data` in container
- Docker Compose mounts `chroma_data` as named volume

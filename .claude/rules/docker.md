# Docker & Deployment

- Multi-stage build: builder (pip install) → runtime (slim)
- CPU-only PyTorch installed first to avoid CUDA bloat
- Health check hits `/api/v1/health` endpoint
- Hugging Face Spaces: Docker SDK, port 7860, free tier (16GB RAM, 2 vCPU)
- Scales to zero after 48h idle, cold start ~30-60s
# Deploy Specification

*Version: 3.0 | Last updated: 2026-07-20*

## Purpose
Deploy HelixDesk to production on Hugging Face Spaces (Docker SDK). Deployment is automatic on git push to the HF Space repo. GitHub Actions CI runs tests and verifies Docker build.

## Trigger
- Push to `main` branch (GitHub repo)
- Push to HF Space repo (auto-deploys)
- Manual trigger via GitHub Actions

## Inputs Required
- Code on `main` branch with passing tests
- HF Space created (Docker SDK, free tier)
- Pinecone index exists (created automatically on first app startup)
- HF Space secrets configured

## Output Definition
- Format: Running HF Space container (Docker, 16GB RAM, 2 vCPU, free tier)
- Quality bar: Health check returns 200, API docs accessible at `https://YOUR_USERNAME-helixdesk.hf.space/api/v1/docs`
- Destination: Hugging Face Spaces free tier (scales to zero after 48h idle, cold start ~30-60s)

## Step-by-Step Process
1. Push code to `main` branch (GitHub)
2. GitHub Actions runs tests (`pytest tests/ -v`) and verifies Docker build
3. Push to HF Space repo (or mirror from GitHub) triggers HF auto-deploy
4. HF builds Docker image, starts container on port 7860
5. Health check verifies `/api/v1/health` with Pinecone connectivity
6. App available at `https://YOUR_USERNAME-helixdesk.hf.space`

## Required GitHub Secrets
None for CI (tests use mocked LLMs).

## Required HF Space Secrets (set in HF Space Settings → Repository secrets)
| Secret | Description |
|--------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM inference |
| `PINECONE_API_KEY` | Pinecone API key for vector database |

## Quality Checklist
- [ ] Tests pass
- [ ] Docker build succeeds
- [ ] HF Space deploy succeeds (check HF Space logs)
- [ ] Health check returns 200 with `pinecone: "reachable"`
- [ ] Swagger UI accessible at `/api/v1/docs`
- [ ] Ticket submission works end-to-end

## Approval Gates
None — automated on push to HF Space repo.

## Error Handling
- Test failure → deploy not triggered, check GitHub Actions logs
- Docker build failure → check CI logs
- HF deploy failure → check HF Space build logs
- Health check failure → Pinecone API key may be invalid, or index not yet created (first deploy creates index)
- Cold start timeout → HF Spaces handles wake-up; first request after 48h idle takes 30-60s

## Common Failure Modes
- Pinecone API key invalid → verify in Pinecone console, update in HF Space secrets
- Pinecone index dimension mismatch → must be 384 for `all-MiniLM-L6-v2`
- HF Space build timeout → Docker image too large; optimize dependencies
- HF Space OOM → free tier has 16GB RAM; should not happen with this app

## Local Development
```bash
# Start with Docker Compose (port 7860)
docker-compose up --build

# Run ingestion (requires PINECONE_API_KEY in .env)
python -m app.rag.ingest
```

## Manual Deploy (if needed)
```bash
# Clone HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/helixdesk
cd helixdesk

# Copy your code, commit, push
git add .
git commit -m "Deploy"
git push  # HF auto-deploys

# View logs in HF Space UI or:
# gh api -X GET /repos/YOUR_USERNAME/helixdesk/actions/runs
```
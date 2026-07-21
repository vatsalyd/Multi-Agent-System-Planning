# Deploy Specification

*Version: 4.0 | Last updated: 2026-07-22*

## Purpose
Deploy HelixDesk to production on Render (free tier). Deployment is automatic on git push to the Render-connected repo. GitHub Actions CI runs tests and verifies Docker build.

## Trigger
- Push to `main` branch (GitHub repo)
- Push to Render-connected repo (auto-deploys)
- Manual trigger via GitHub Actions

## Inputs Required
- Code on `main` branch with passing tests
- Render account (free, no credit card)
- Pinecone index exists (created automatically on first app startup)
- Render environment variables configured

## Output Definition
- Format: Running Render web service container (Docker, 512MB RAM, 0.1 CPU, free tier)
- Quality bar: Health check returns 200, API docs accessible at `https://helixdesk.onrender.com/api/v1/docs`
- Destination: Render free tier (scales to zero after 15min idle, cold start ~30-50s)

## Step-by-Step Process
1. Push code to `main` branch (GitHub)
2. GitHub Actions runs tests (`pytest tests/ -v`) and verifies Docker build
3. Push to Render-connected repo (or mirror from GitHub) triggers Render auto-deploy
4. Render builds Docker image, starts container on port from `$PORT` env var (8000)
5. Health check verifies `/api/v1/health` with Pinecone connectivity
6. App available at `https://helixdesk.onrender.com`

## Required GitHub Secrets
None for CI (tests use mocked LLMs).

## Required Render Environment Variables (set in Render Dashboard → Settings → Environment)
| Secret | Description |
|--------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM inference |
| `PINECONE_API_KEY` | Pinecone API key for vector database |

Additional config via `render.yaml`:
| Variable | Value |
|----------|-------|
| `PINECONE_INDEX_NAME` | `helixdesk` |
| `PINECONE_EMBEDDING_MODEL` | `multilingual-e5-large` |
| `LOG_LEVEL` | `INFO` |
| `HOST` | `0.0.0.0` |
| `PORT` | `8000` |

## Quality Checklist
- [ ] Tests pass
- [ ] Docker build succeeds
- [ ] Render deploy succeeds (check Render logs)
- [ ] Health check returns 200 with `pinecone: "reachable"`
- [ ] Swagger UI accessible at `/api/v1/docs`
- [ ] Ticket submission works end-to-end

## Approval Gates
None — automated on push to Render-connected repo.

## Error Handling
- Test failure → deploy not triggered, check GitHub Actions logs
- Docker build failure → check CI logs
- Render deploy failure → check Render build logs
- Health check failure → Pinecone API key may be invalid, or index not yet created (first deploy creates index)
- Cold start timeout → Render handles wake-up; first request after 15min idle takes 30-50s

## Common Failure Modes
- Pinecone API key invalid → verify in Pinecone console, update in Render secrets
- Pinecone index dimension mismatch → must be 1024 for `multilingual-e5-large` (index auto-recreated on deploy)
- Render build timeout → Docker image too large; current image ~468MB is fine
- Render OOM → free tier has 512MB RAM; should not happen with current app (~50MB runtime)

## Local Development
```bash
# Start with Docker Compose (port 8000)
docker-compose up --build

# Run ingestion (requires PINECONE_API_KEY in .env)
python -m app.rag.ingest
```

## Manual Deploy (if needed)
```bash
# Render auto-deploys on push to connected repo
# Or use Render CLI:
# render deploy helixdesk
```

## Keep-Alive (Optional)
To prevent 15min idle spin-down and eliminate cold starts:
- Add a free cron job (cron-job.org, cronjob.run, UptimeRobot) hitting `/healthz` every 30 minutes
- Costs ~240 hrs/mo of 750 hrs free budget
- No code changes needed — purely external config
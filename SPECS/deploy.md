# Deploy Specification

*Version: 2.0 | Last updated: 2026-07-20*

## Purpose
Deploy HelixDesk to production via GitHub Actions CI/CD pipeline: push to main → test → deploy to Fly.io (Pinecone is managed cloud, no deployment needed).

## Trigger
- Push to `main` branch
- Manual trigger via GitHub Actions

## Inputs Required
- All GitHub Secrets configured (see below)
- Code on `main` branch with passing tests
- Fly.io app created (`fly launch` once)
- Pinecone index exists (created automatically on first app startup)

## Output Definition
- Format: Running Fly.io Machine in `iad` region
- Quality bar: Health check returns 200, API docs accessible at `https://helixdesk.fly.dev/api/v1/docs`
- Destination: Fly.io free tier (shared-cpu-1x, 256MB RAM, auto-stop on idle)

## Step-by-Step Process
1. Push code to `main` branch
2. GitHub Actions runs tests (`pytest tests/ -v`)
3. On test pass: `flyctl deploy --remote-only` builds Docker image on Fly.io builders and deploys
4. Fly.io starts Machine, health check verifies `/api/v1/health`
5. App scales to zero when idle, cold-starts on first request (~3-8s)

## Required GitHub Secrets
| Secret | Description |
|--------|-------------|
| `FLY_API_TOKEN` | Fly.io API token (from `fly tokens create`) |

## Required Fly.io App Secrets (set via `fly secrets set`)
| Secret | Description |
|--------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM inference |
| `PINECONE_API_KEY` | Pinecone API key for vector database |

## Quality Checklist
- [ ] Tests pass before deploy
- [ ] Fly.io deploy succeeds
- [ ] Health check returns 200 with `pinecone: "reachable"`
- [ ] Swagger UI accessible at `/api/v1/docs`
- [ ] Ticket submission works end-to-end

## Approval Gates
None — automated on push to main.

## Error Handling
- Test failure → deploy skipped, check GitHub Actions logs
- Fly.io deploy failure → check `flyctl` logs, verify secrets are set
- Health check failure → Pinecone API key may be invalid, or index not yet created (first deploy creates index)
- Cold start timeout → increase `start_period` in health check if needed

## Common Failure Modes
- Fly.io token expired → regenerate with `fly tokens create`
- Pinecone API key invalid → verify in Pinecone console, update via `fly secrets set`
- Pinecone index dimension mismatch → must be 384 for `all-MiniLM-L6-v2`
- Fly.io free tier limits exceeded → scale to paid plan or wait for reset

## Local Development
```bash
# Start with Docker Compose
docker-compose up --build

# Run ingestion (requires PINECONE_API_KEY in .env)
python -m app.rag.ingest
```

## Manual Deploy (if needed)
```bash
flyctl deploy --remote-only
flyctl logs  # tail logs
flyctl status  # check app status
```
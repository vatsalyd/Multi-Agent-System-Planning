# Deploy Specification

*Version: 1.0 | Last updated: 2026-07-11*

## Purpose
Deploy HelixDesk to production via GitHub Actions CI/CD pipeline: push to main → test → build Docker image → push to ECR → deploy to EC2.

## Trigger
- Push to `main` branch
- Manual trigger via GitHub Actions

## Inputs Required
- All GitHub Secrets configured (see below)
- Code on `main` branch with passing tests

## Output Definition
- Format: Running Docker container on EC2
- Quality bar: Health check returns 200, API docs accessible at `http://[EC2_IP]:8000/api/v1/docs`
- Destination: AWS EC2 instance

## Step-by-Step Process
1. Push code to `main` branch
2. GitHub Actions runs tests (`pytest tests/ -v`)
3. On test pass: build Docker image with commit SHA tag
4. Push image to ECR repository
5. SSH into EC2, pull new image, stop old container, start new one
6. Wait 10s for startup, then health check

## Required GitHub Secrets
| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM credentials for ECR |
| `AWS_SECRET_ACCESS_KEY` | IAM credentials for ECR |
| `AWS_REGION` | e.g., us-east-1 |
| `ECR_REPOSITORY` | ECR repo name (e.g., multi-agent-triage) |
| `EC2_HOST` | EC2 Elastic IP |
| `EC2_USER` | SSH user (e.g., ec2-user) |
| `EC2_SSH_KEY` | Private key (.pem contents) |
| `GROQ_API_KEY` | Groq API key for LLM inference |

## Quality Checklist
- [ ] Tests pass before build
- [ ] Docker image builds successfully
- [ ] Image pushed to ECR with SHA tag + latest
- [ ] EC2 pulls new image
- [ ] Old container stopped and removed
- [ ] Health check returns 200
- [ ] Swagger UI accessible at `/api/v1/docs`

## Approval Gates
None — automated on push to main.

## Error Handling
- Test failure → build/deploy skipped, check GitHub Actions logs
- ECR push failure → check AWS credentials and ECR repo existence
- EC2 SSH failure → check EC2 host, user, and SSH key
- Health check failure → container may need more startup time (model loading ~60s)

## Common Failure Modes
- AWS credentials expired → rotate IAM keys
- EC2 instance stopped → start instance first
- Docker image too large → multi-stage build keeps it lean (~500MB)
- ChromaDB data lost → EC2 uses named volume `multi-agent-chroma`

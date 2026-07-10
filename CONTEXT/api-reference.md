# HelixDesk API Reference

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/tickets` | Full pipeline: triage → retrieve → resolve |
| POST | `/api/v1/tickets/triage` | Classification only |
| GET | `/api/v1/health` | Health check with version |
| GET | `/healthz` | Liveness probe |
| GET | `/api/v1/docs` | Swagger UI |

## POST /api/v1/tickets

**Request:**
```json
{
  "ticket_text": "I forgot my VPN password and cannot connect remotely.",
  "source": "slack",
  "metadata": {}
}
```

**Response:**
```json
{
  "ticket_id": "a1b2c3d4-...",
  "category": "IT_SUPPORT",
  "confidence": 0.92,
  "summary": "Employee unable to access VPN due to forgotten password.",
  "resolution": "To reset your VPN password...",
  "sources": ["vpn_setup_guide.md"],
  "status": "resolved",
  "processing_time_ms": 1840
}
```

## Status Values
- `pending` → initial
- `triaged` → classified
- `documents_retrieved` → docs found
- `resolved` → full pipeline complete
- `escalated` → low confidence, human review
- `error` / `retrieval_error` / `resolution_error` → failures

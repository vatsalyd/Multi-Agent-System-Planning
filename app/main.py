"""
FastAPI application — the production API layer.

This wraps the entire multi-agent system in a REST API that external
systems (Slack bots, email parsers, ticketing systems, webhooks) can
call to process support tickets.

Endpoints:
    POST /api/v1/tickets         — Full pipeline: triage → retrieve → resolve
    POST /api/v1/tickets/triage  — Triage only (classification without resolution)
    GET  /api/v1/health          — Health check
"""

import logging
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    TicketRequest,
    TriageResult,
    ResolutionResponse,
    HealthResponse,
    ErrorResponse,
)
from app.agents.triage import triage_ticket
from app.agents.graph import process_ticket

# ── Logging Setup ───────────────────────────────────────────
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI App ─────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A multi-agent AI system that autonomously triages incoming "
        "corporate requests, routes them to specialized agents, and "
        "generates data-backed resolution drafts using internal "
        "knowledge bases."
    ),
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# ── CORS Middleware ─────────────────────────────────────────
# Allow all origins for development. Restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ───────────────────────────────────────────────


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
    description="Returns the health status and version of the service.",
)
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        service=settings.app_name,
    )


@app.post(
    "/api/v1/tickets",
    response_model=ResolutionResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Tickets"],
    summary="Submit a Ticket",
    description=(
        "Submit a support ticket for full processing through the "
        "multi-agent pipeline: Triage → Retrieval → Resolution."
    ),
)
async def submit_ticket(request: TicketRequest):
    """
    Process a ticket through the full agent pipeline.

    1. Triage Agent classifies the ticket
    2. Retrieval Agent finds relevant documentation
    3. Resolution Agent drafts a response

    If confidence is too low, the ticket is escalated to a human.
    """
    logger.info(
        f"Received ticket from source: {request.source} — "
        f"{request.ticket_text[:80]}..."
    )

    try:
        # Run the full LangGraph pipeline
        result = process_ticket(
            ticket_text=request.ticket_text,
            source=request.source,
        )

        return ResolutionResponse(
            ticket_id=result["ticket_id"],
            category=result["category"],
            confidence=result["confidence"],
            summary=result["summary"],
            resolution=result["resolution"],
            sources=result.get("sources", []),
            status=result["status"],
            processing_time_ms=result["processing_time_ms"],
        )

    except Exception as e:
        logger.error(f"Failed to process ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process ticket: {str(e)}",
        )


@app.post(
    "/api/v1/tickets/triage",
    response_model=TriageResult,
    responses={500: {"model": ErrorResponse}},
    tags=["Tickets"],
    summary="Triage Only",
    description=(
        "Classify a ticket without generating a resolution. "
        "Useful for routing or analytics."
    ),
)
async def triage_only(request: TicketRequest):
    """
    Classify a ticket without running the full pipeline.

    Returns only the triage result: category, confidence, and summary.
    """
    logger.info(f"Triage-only request: {request.ticket_text[:80]}...")

    try:
        # Run only the Triage Agent
        result = triage_ticket(request.ticket_text)
        ticket_id = str(uuid.uuid4())

        return TriageResult(
            ticket_id=ticket_id,
            category=result["category"],
            confidence=result["confidence"],
            summary=result["summary"],
            status="triaged",
        )

    except Exception as e:
        logger.error(f"Failed to triage ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to triage ticket: {str(e)}",
        )


# ── Startup Event ───────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info(
        f"{settings.app_name} v{settings.app_version} started "
        f"on {settings.host}:{settings.port}"
    )
    if not settings.groq_api_key:
        logger.warning(
            "GROQ_API_KEY is not set! "
            "API calls to agents will fail."
        )

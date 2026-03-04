"""
FastAPI application — REST API for the multi-agent triage system.
"""

import logging
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

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

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/v1/docs")


@app.get(
    "/healthz",
    tags=["System"],
    summary="Liveness Probe",
)
async def liveness():
    return {"status": "ok"}


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
)
async def health_check():
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
)
async def submit_ticket(request: TicketRequest):
    """Process a ticket through the full agent pipeline: Triage → Retrieval → Resolution."""
    logger.info(
        f"Received ticket from source: {request.source} — "
        f"{request.ticket_text[:80]}..."
    )

    try:
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
)
async def triage_only(request: TicketRequest):
    """Classify a ticket without running the full pipeline."""
    logger.info(f"Triage-only request: {request.ticket_text[:80]}...")

    try:
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


@app.on_event("startup")
async def startup_event():
    logger.info(
        f"{settings.app_name} v{settings.app_version} started "
        f"on {settings.host}:{settings.port}"
    )
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY is not set! API calls to agents will fail.")

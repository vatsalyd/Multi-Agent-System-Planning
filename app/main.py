"""
FastAPI application — REST API for the multi-agent triage system.
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.logging_config import setup_logging, get_logger, correlation_id
from app.models import (
    TicketRequest,
    TriageResult,
    ResolutionResponse,
    HealthResponse,
    ErrorResponse,
)
from app.agents.triage import triage_ticket
from app.agents.graph import process_ticket

setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup checks, then yield, then shutdown."""
    # Startup
    logger.info(
        "%s v%s started on %s:%s",
        settings.app_name,
        settings.app_version,
        settings.host,
        settings.port,
    )
    if not settings.groq_api_key:
        logger.warning(
            "GROQ_API_KEY is not set! API calls to agents will fail."
        )

    # Pinecone connectivity check (fail fast)
    try:
        from app.rag.vectorstore import get_pinecone_client
        pc = get_pinecone_client()
        index = pc.Index(settings.pinecone_index_name)
        index.describe_index_stats()
        logger.info("Pinecone connectivity verified")
    except Exception as e:
        logger.error("Pinecone connectivity check failed: %s", e)
        # Don't raise — let health endpoint report degraded
        # raise RuntimeError(f"ChromaDB unreachable: {e}") from e

    yield

    # Shutdown (if needed)
    logger.info("Shutting down %s", settings.app_name)


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
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Propagate correlation ID from header or generate one."""
    cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    token = correlation_id.set(cid)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    correlation_id.reset(token)
    return response


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
    """Verify Groq API key is set and Pinecone is reachable."""
    checks = {}

    # Groq API key check
    if settings.groq_api_key:
        checks["groq_api_key"] = "configured"
    else:
        checks["groq_api_key"] = "missing"

    # ChromaDB check
    try:
        from app.rag.vectorstore import get_pinecone_client
        pc = get_pinecone_client()
        index = pc.Index(settings.pinecone_index_name)
        index.describe_index_stats()
        checks["pinecone"] = "reachable"
    except Exception as e:
        checks["pinecone"] = f"error: {e}"

    overall = (
        "healthy"
        if all(v == "configured" or v == "reachable" for v in checks.values())
        else "degraded"
    )

    return HealthResponse(
        status=overall,
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
        "Received ticket from source: %s — %s...",
        request.source,
        request.ticket_text[:80],
    )

    try:
        result = await process_ticket(
            ticket_text=request.ticket_text,
            source=request.source,
        )

        logger.info(
            "Ticket processed: category=%s confidence=%.2f time_ms=%d",
            result["category"],
            result["confidence"],
            result["processing_time_ms"],
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
        logger.error("Failed to process ticket: %s", e, exc_info=True)
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
    logger.info("Triage-only request: %s...", request.ticket_text[:80])

    try:
        result = await triage_ticket(request.ticket_text)
        ticket_id = str(uuid.uuid4())

        return TriageResult(
            ticket_id=ticket_id,
            category=result["category"],
            confidence=result["confidence"],
            summary=result["summary"],
            status="triaged",
        )

    except Exception as e:
        logger.error("Failed to triage ticket: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to triage ticket: {str(e)}",
        )
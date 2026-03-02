"""
Pydantic models for the FastAPI request/response schemas.

These enforce type safety at the API boundary — invalid requests
are rejected with clear error messages before they reach any agent.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Request Models ──────────────────────────────────────────

class TicketRequest(BaseModel):
    """Incoming ticket submission payload."""

    ticket_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The text content of the support ticket",
        examples=["I forgot my VPN password and cannot connect remotely."],
    )
    source: str = Field(
        default="api",
        description="Source of the ticket (e.g., 'webhook', 'slack', 'email')",
        examples=["webhook"],
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Optional metadata for the ticket",
    )


# ── Response Models ─────────────────────────────────────────

class TriageResult(BaseModel):
    """Result from triage-only endpoint."""

    ticket_id: str
    category: str
    confidence: float
    summary: str
    status: str


class ResolutionResponse(BaseModel):
    """Full resolution response from the agent pipeline."""

    ticket_id: str
    category: str
    confidence: float
    summary: str
    resolution: str
    sources: list[str]
    status: str
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    service: str


class ErrorResponse(BaseModel):
    """Error response for failed requests."""

    error: str
    detail: Optional[str] = None

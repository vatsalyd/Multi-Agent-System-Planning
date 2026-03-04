"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TicketRequest(BaseModel):
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


class TriageResult(BaseModel):
    ticket_id: str
    category: str
    confidence: float
    summary: str
    status: str


class ResolutionResponse(BaseModel):
    ticket_id: str
    category: str
    confidence: float
    summary: str
    resolution: str
    sources: list[str]
    status: str
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    service: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

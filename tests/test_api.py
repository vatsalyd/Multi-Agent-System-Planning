"""
Integration tests for the FastAPI endpoints.

Tests the API endpoints return correct status codes, response shapes,
and handle malformed input gracefully. The agent pipeline is mocked
to avoid external API calls.
"""

from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Health Check Tests ──────────────────────────────────────

class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_returns_200(self):
        """Health check should always return 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_shape(self):
        """Health response should have status, version, and service."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "service" in data


# ── Ticket Submission Tests ─────────────────────────────────

class TestTicketEndpoint:
    """Tests for POST /api/v1/tickets."""

    @patch("app.main.process_ticket")
    def test_submit_ticket_returns_200(self, mock_process):
        """Valid ticket should return 200 with resolution."""
        mock_process.return_value = {
            "ticket_id": "test-123",
            "category": "IT_SUPPORT",
            "confidence": 0.95,
            "summary": "VPN issue",
            "resolution": "Reset your VPN password via the portal.",
            "sources": ["vpn_setup_guide.md"],
            "status": "resolved",
            "processing_time_ms": 1500.0,
        }

        response = client.post(
            "/api/v1/tickets",
            json={
                "ticket_text": "I cannot connect to the VPN from home. I have tried restarting.",
                "source": "test",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "IT_SUPPORT"
        assert data["confidence"] == 0.95
        assert "resolution" in data
        assert len(data["sources"]) > 0

    def test_rejects_empty_ticket_text(self):
        """Ticket with empty text should be rejected."""
        response = client.post(
            "/api/v1/tickets",
            json={"ticket_text": ""},
        )
        assert response.status_code == 422

    def test_rejects_too_short_ticket(self):
        """Ticket with text shorter than 10 chars should be rejected."""
        response = client.post(
            "/api/v1/tickets",
            json={"ticket_text": "Help"},
        )
        assert response.status_code == 422

    def test_rejects_missing_ticket_text(self):
        """Request without ticket_text field should be rejected."""
        response = client.post(
            "/api/v1/tickets",
            json={"source": "test"},
        )
        assert response.status_code == 422


# ── Triage-Only Tests ───────────────────────────────────────

class TestTriageEndpoint:
    """Tests for POST /api/v1/tickets/triage."""

    @patch("app.main.triage_ticket")
    def test_triage_only_returns_200(self, mock_triage):
        """Triage-only should return classification without resolution."""
        mock_triage.return_value = {
            "category": "HR_POLICY",
            "confidence": 0.88,
            "summary": "Employee asking about leave",
        }

        response = client.post(
            "/api/v1/tickets/triage",
            json={
                "ticket_text": "How many days of annual leave do I get per year?",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "HR_POLICY"
        assert "resolution" not in data
        assert "ticket_id" in data

    @patch("app.main.triage_ticket")
    def test_triage_handles_agent_error(self, mock_triage):
        """Server errors during triage should return 500."""
        mock_triage.side_effect = Exception("LLM connection failed")

        response = client.post(
            "/api/v1/tickets/triage",
            json={
                "ticket_text": "Some test ticket for triage testing purposes.",
            },
        )

        assert response.status_code == 500

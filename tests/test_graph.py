"""
Tests for LangGraph orchestration — routing logic and process_ticket.
"""

import pytest
from unittest.mock import patch, AsyncMock

from app.agents.graph import process_ticket, should_escalate


class TestShouldEscalate:
    def test_low_confidence_escalates(self):
        assert should_escalate({"confidence": 0.3}) == "escalate"

    def test_high_confidence_retrieves(self):
        assert should_escalate({"confidence": 0.8}) == "retrieve"

    def test_exact_threshold_retrieves(self):
        assert should_escalate({"confidence": 0.5}) == "retrieve"

    def test_zero_confidence_escalates(self):
        assert should_escalate({"confidence": 0.0}) == "escalate"

    def test_missing_confidence_escalates(self):
        assert should_escalate({}) == "escalate"


class TestProcessTicket:
    @pytest.mark.asyncio
    @patch("app.agents.graph.generate_resolution")
    @patch("app.agents.graph.retrieve_documents")
    @patch("app.agents.graph.triage_ticket")
    async def test_happy_path(
        self, mock_triage, mock_retrieve, mock_resolve
    ):
        mock_triage.return_value = {
            "category": "IT_SUPPORT",
            "confidence": 0.9,
            "summary": "VPN issue",
        }
        mock_retrieve.return_value = [
            {"content": "Reset your VPN password via IT portal.", "source": "vpn.md"},
        ]
        mock_resolve.return_value = {
            "resolution": "Reset your VPN password.",
            "sources": ["vpn_guide.md"],
        }

        result = await process_ticket("My VPN is broken", source="slack")

        assert result["category"] == "IT_SUPPORT"
        assert result["confidence"] == 0.9
        assert result["status"] == "resolved"
        assert result["resolution"] == "Reset your VPN password."
        assert result["sources"] == ["vpn_guide.md"]
        assert result["processing_time_ms"] > 0

    @pytest.mark.asyncio
    @patch("app.agents.graph.triage_ticket")
    async def test_escalation_on_low_confidence(self, mock_triage):
        mock_triage.return_value = {
            "category": "GENERAL",
            "confidence": 0.2,
            "summary": "Unclear request",
        }

        result = await process_ticket("Something weird", source="email")

        assert result["status"] == "escalated"
        assert result["confidence"] == 0.2
        assert "human review" in result["resolution"].lower()

    @pytest.mark.asyncio
    @patch("app.agents.graph.triage_ticket")
    async def test_triage_error_falls_back(self, mock_triage):
        mock_triage.side_effect = RuntimeError("LLM timeout")

        result = await process_ticket("Test ticket")

        # Triage error sets confidence=0.0, which triggers escalation path
        assert result["status"] == "escalated"
        assert result["error"] == "LLM timeout"

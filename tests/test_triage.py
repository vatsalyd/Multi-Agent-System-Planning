"""
Unit tests for the Triage Agent.

Tests that the Triage Agent correctly classifies sample tickets into
expected categories. All LLM API calls are mocked.
"""

import json
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from app.agents.triage import triage_ticket, CATEGORIES
from tests.conftest import mock_triage_response


# ── Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.agents.triage.create_llm")
class TestTriageAgent:
    """Test suite for the Triage Agent."""

    async def test_classifies_it_support(self, mock_factory):
        """IT-related tickets should be classified as IT_SUPPORT."""
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_triage_response(
            "IT_SUPPORT", 0.95, "Employee cannot connect to VPN"
        )
        mock_factory.return_value = mock_instance

        result = await triage_ticket(
            "I can't connect to the VPN. I've tried restarting my laptop."
        )

        assert result["category"] == "IT_SUPPORT"
        assert result["confidence"] == 0.95
        assert "summary" in result

    async def test_classifies_hr_policy(self, mock_factory):
        """HR-related tickets should be classified as HR_POLICY."""
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_triage_response(
            "HR_POLICY", 0.9, "Employee asking about parental leave"
        )
        mock_factory.return_value = mock_instance

        result = await triage_ticket(
            "How many weeks of parental leave do I get as a primary caregiver?"
        )

        assert result["category"] == "HR_POLICY"
        assert result["confidence"] >= 0.5

    async def test_classifies_expense(self, mock_factory):
        """Expense-related tickets should be classified as EXPENSE."""
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_triage_response(
            "EXPENSE", 0.88, "Employee needs reimbursement for travel"
        )
        mock_factory.return_value = mock_instance

        result = await triage_ticket(
            "I need to submit a reimbursement for my flight to the NYC office."
        )

        assert result["category"] == "EXPENSE"

    async def test_classifies_onboarding(self, mock_factory):
        """Onboarding tickets should be classified as ONBOARDING."""
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_triage_response(
            "ONBOARDING", 0.85, "New employee needs system access"
        )
        mock_factory.return_value = mock_instance

        result = await triage_ticket(
            "I'm a new hire starting next week. What do I need to set up?"
        )

        assert result["category"] == "ONBOARDING"

    async def test_fallback_on_unknown_category(self, mock_factory):
        """Unknown categories from LLM should default to GENERAL."""
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_triage_response(
            "UNKNOWN_CATEGORY", 0.5, "Some ticket"
        )
        mock_factory.return_value = mock_instance

        result = await triage_ticket("Some ambiguous request")

        assert result["category"] == "GENERAL"
        assert result["confidence"] == 0.3

    async def test_fallback_on_invalid_json(self, mock_factory):
        """Invalid JSON from LLM should return safe defaults."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "This is not valid JSON"
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        result = await triage_ticket("Some ticket text")

        assert result["category"] == "GENERAL"
        assert result["confidence"] == 0.0


def test_all_categories_are_valid():
    """Verify all defined categories are valid strings."""
    assert len(CATEGORIES) == 5
    for cat in CATEGORIES:
        assert isinstance(cat, str)
        assert cat == cat.upper()

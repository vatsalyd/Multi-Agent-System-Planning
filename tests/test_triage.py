"""
Unit tests for the Triage Agent.

Tests that the Triage Agent correctly classifies sample tickets into
expected categories. All OpenAI API calls are mocked — these tests run
without an API key.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from app.agents.triage import triage_ticket, CATEGORIES


# ── Mock Helpers ────────────────────────────────────────────

def mock_llm_response(category: str, confidence: float, summary: str):
    """Create a mock LLM response with the given triage result."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "category": category,
        "confidence": confidence,
        "summary": summary,
    })
    return mock_response


# ── Tests ───────────────────────────────────────────────────

@patch("app.agents.triage.ChatGroq")
class TestTriageAgent:
    """Test suite for the Triage Agent."""

    def test_classifies_it_support(self, mock_chat):
        """IT-related tickets should be classified as IT_SUPPORT."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = mock_llm_response(
            "IT_SUPPORT", 0.95, "Employee cannot connect to VPN"
        )
        mock_chat.return_value = mock_instance

        result = triage_ticket(
            "I can't connect to the VPN. I've tried restarting my laptop."
        )

        assert result["category"] == "IT_SUPPORT"
        assert result["confidence"] == 0.95
        assert "summary" in result

    def test_classifies_hr_policy(self, mock_chat):
        """HR-related tickets should be classified as HR_POLICY."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = mock_llm_response(
            "HR_POLICY", 0.9, "Employee asking about parental leave"
        )
        mock_chat.return_value = mock_instance

        result = triage_ticket(
            "How many weeks of parental leave do I get as a primary caregiver?"
        )

        assert result["category"] == "HR_POLICY"
        assert result["confidence"] >= 0.5

    def test_classifies_expense(self, mock_chat):
        """Expense-related tickets should be classified as EXPENSE."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = mock_llm_response(
            "EXPENSE", 0.88, "Employee needs reimbursement for travel"
        )
        mock_chat.return_value = mock_instance

        result = triage_ticket(
            "I need to submit a reimbursement for my flight to the NYC office."
        )

        assert result["category"] == "EXPENSE"

    def test_classifies_onboarding(self, mock_chat):
        """Onboarding tickets should be classified as ONBOARDING."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = mock_llm_response(
            "ONBOARDING", 0.85, "New employee needs system access"
        )
        mock_chat.return_value = mock_instance

        result = triage_ticket(
            "I'm a new hire starting next week. What do I need to set up?"
        )

        assert result["category"] == "ONBOARDING"

    def test_fallback_on_unknown_category(self, mock_chat):
        """Unknown categories from LLM should default to GENERAL."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = mock_llm_response(
            "UNKNOWN_CATEGORY", 0.5, "Some ticket"
        )
        mock_chat.return_value = mock_instance

        result = triage_ticket("Some ambiguous request")

        assert result["category"] == "GENERAL"
        assert result["confidence"] == 0.3  # Lowered confidence on fallback

    def test_fallback_on_invalid_json(self, mock_chat):
        """Invalid JSON from LLM should return safe defaults."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is not valid JSON"
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        result = triage_ticket("Some ticket text")

        assert result["category"] == "GENERAL"
        assert result["confidence"] == 0.0

    def test_all_categories_are_valid(self, mock_chat):
        """Verify all defined categories are valid strings."""
        assert len(CATEGORIES) == 5
        for cat in CATEGORIES:
            assert isinstance(cat, str)
            assert cat == cat.upper()  # All caps convention

"""
Unit tests for the Resolution Agent.

Tests that the Resolution Agent generates non-empty resolution drafts
with citations when given ticket context and retrieved documents.
All LLM calls are mocked.
"""

from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from app.agents.resolution import generate_resolution


# ── Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.agents.resolution.create_llm")
class TestResolutionAgent:
    """Test suite for the Resolution Agent."""

    async def test_generates_resolution_with_sources(self, mock_factory):
        """Should generate a non-empty resolution with source citations."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = (
            "RESOLUTION:\n"
            "Thank you for reaching out. To reset your VPN password, "
            "please visit the IT Self-Service Portal [Source: vpn_setup_guide.md]. "
            "If the issue persists, contact the IT Help Desk at ext. 4500.\n\n"
            "SOURCES:\n"
            "- vpn_setup_guide.md\n"
            "- password_reset_policy.md"
        )
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        docs = [
            {
                "content": "Visit the IT Self-Service Portal for password reset.",
                "source": "vpn_setup_guide.md",
            },
            {
                "content": "Passwords expire every 90 days.",
                "source": "password_reset_policy.md",
            },
        ]

        result = await generate_resolution(
            ticket_text="I forgot my VPN password",
            category="IT_SUPPORT",
            retrieved_docs=docs,
        )

        assert "resolution" in result
        assert len(result["resolution"]) > 0
        assert "sources" in result
        assert len(result["sources"]) > 0

    async def test_handles_empty_retrieved_docs(self, mock_factory):
        """Should still generate a resolution even with no retrieved docs."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = (
            "RESOLUTION:\n"
            "We were unable to find specific policy documentation for your "
            "request. Please contact the HR department at hr@company.com.\n\n"
            "SOURCES:\n"
            "None"
        )
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        result = await generate_resolution(
            ticket_text="Some obscure question",
            category="GENERAL",
            retrieved_docs=[],
        )

        assert "resolution" in result
        assert len(result["resolution"]) > 0

    async def test_sources_are_deduplicated(self, mock_factory):
        """Sources from multiple docs should be deduplicated."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "RESOLUTION:\nSome resolution text.\n\nSOURCES:\n- doc.md"
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        docs = [
            {"content": "Chunk 1", "source": "leave_policy.md"},
            {"content": "Chunk 2", "source": "leave_policy.md"},
        ]

        result = await generate_resolution(
            ticket_text="How much leave do I get?",
            category="HR_POLICY",
            retrieved_docs=docs,
        )

        assert len(result["sources"]) == 1
        assert result["sources"][0] == "leave_policy.md"

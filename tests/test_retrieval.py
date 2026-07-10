"""
Unit tests for the Retrieval Agent.

Tests that the Retrieval Agent correctly constructs optimized queries
and retrieves relevant documents. All external calls (LLM, ChromaDB)
are mocked.
"""

from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from app.agents.retrieval import retrieve_documents
from app.rag.vectorstore import RetrievedChunk
from tests.conftest import mock_documents


# ── Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.agents.retrieval.similarity_search")
@patch("app.agents.retrieval.create_llm")
class TestRetrievalAgent:
    """Test suite for the Retrieval Agent."""

    async def test_retrieves_documents_for_it_ticket(
        self, mock_factory, mock_search
    ):
        """Should retrieve relevant docs for an IT support ticket."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "VPN connection troubleshooting password reset"
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        mock_search.return_value = mock_documents(3)

        result = await retrieve_documents(
            ticket_text="I can't connect to the VPN",
            category="IT_SUPPORT",
            k=3,
        )

        assert len(result) == 3
        assert all(isinstance(doc, RetrievedChunk) for doc in result)
        assert all(hasattr(doc, "content") for doc in result)
        assert all(hasattr(doc, "source") for doc in result)
        mock_search.assert_called_once()

    async def test_returns_empty_on_no_results(self, mock_factory, mock_search):
        """Should return empty list when no documents match."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "some query"
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        mock_search.return_value = []

        result = await retrieve_documents(
            ticket_text="Something very unusual",
            category="GENERAL",
        )

        assert result == []

    async def test_respects_k_parameter(self, mock_factory, mock_search):
        """Should pass the k parameter to similarity search."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "optimized query"
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        mock_search.return_value = mock_documents(2)

        await retrieve_documents(
            ticket_text="Need help with expenses",
            category="EXPENSE",
            k=2,
        )

        mock_search.assert_called_once_with("optimized query", k=2)

    async def test_result_format(self, mock_factory, mock_search):
        """Results should be RetrievedChunk with content and source."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "test query"
        mock_instance.ainvoke.return_value = mock_response
        mock_factory.return_value = mock_instance

        mock_search.return_value = mock_documents(1)

        result = await retrieve_documents("test", "GENERAL", k=1)

        assert len(result) == 1
        assert result[0].content == "This is document chunk 1 content."
        assert result[0].source == "policy_1.md"

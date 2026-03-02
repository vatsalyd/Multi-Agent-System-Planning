"""
Unit tests for the Retrieval Agent.

Tests that the Retrieval Agent correctly constructs optimized queries
and retrieves relevant documents. All external calls (OpenAI, ChromaDB)
are mocked.
"""

from unittest.mock import patch, MagicMock

import pytest

from app.agents.retrieval import retrieve_documents


# ── Mock Helpers ────────────────────────────────────────────

def mock_documents(n: int = 3):
    """Create a list of mock LangChain Document objects."""
    docs = []
    for i in range(n):
        doc = MagicMock()
        doc.page_content = f"This is document chunk {i + 1} content."
        doc.metadata = {"source": f"policy_{i + 1}.md"}
        docs.append(doc)
    return docs


# ── Tests ───────────────────────────────────────────────────

@patch("app.agents.retrieval.similarity_search")
@patch("app.agents.retrieval.ChatGroq")
class TestRetrievalAgent:
    """Test suite for the Retrieval Agent."""

    def test_retrieves_documents_for_it_ticket(
        self, mock_chat, mock_search
    ):
        """Should retrieve relevant docs for an IT support ticket."""
        # Mock the LLM query optimizer
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "VPN connection troubleshooting password reset"
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        # Mock ChromaDB search results
        mock_search.return_value = mock_documents(3)

        result = retrieve_documents(
            ticket_text="I can't connect to the VPN",
            category="IT_SUPPORT",
            k=3,
        )

        assert len(result) == 3
        assert all("content" in doc for doc in result)
        assert all("source" in doc for doc in result)
        mock_search.assert_called_once()

    def test_returns_empty_on_no_results(self, mock_chat, mock_search):
        """Should return empty list when no documents match."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "some query"
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        mock_search.return_value = []

        result = retrieve_documents(
            ticket_text="Something very unusual",
            category="GENERAL",
        )

        assert result == []

    def test_respects_k_parameter(self, mock_chat, mock_search):
        """Should pass the k parameter to similarity search."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "optimized query"
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        mock_search.return_value = mock_documents(2)

        retrieve_documents(
            ticket_text="Need help with expenses",
            category="EXPENSE",
            k=2,
        )

        mock_search.assert_called_once_with("optimized query", k=2)

    def test_result_format(self, mock_chat, mock_search):
        """Results should have 'content' and 'source' keys."""
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "test query"
        mock_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_instance

        mock_search.return_value = mock_documents(1)

        result = retrieve_documents("test", "GENERAL", k=1)

        assert len(result) == 1
        assert "content" in result[0]
        assert "source" in result[0]
        assert result[0]["source"] == "policy_1.md"

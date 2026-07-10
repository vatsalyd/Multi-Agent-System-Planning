"""
Shared test fixtures and helpers.
"""

import json
from unittest.mock import MagicMock


def mock_llm_response(content: str) -> MagicMock:
    """Create a mock LLM response with the given content."""
    mock_response = MagicMock()
    mock_response.content = content
    return mock_response


def mock_triage_response(category: str, confidence: float, summary: str) -> MagicMock:
    """Create a mock LLM response with a triage JSON result."""
    return mock_llm_response(json.dumps({
        "category": category,
        "confidence": confidence,
        "summary": summary,
    }))


def mock_documents(n: int = 3) -> list:
    """Create a list of mock LangChain Document objects."""
    docs = []
    for i in range(n):
        doc = MagicMock()
        doc.page_content = f"This is document chunk {i + 1} content."
        doc.metadata = {"source": f"policy_{i + 1}.md"}
        docs.append(doc)
    return docs

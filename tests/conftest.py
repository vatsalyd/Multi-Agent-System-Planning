"""
Shared test fixtures and helpers.
"""

import json
from unittest.mock import MagicMock

from app.rag.vectorstore import RetrievedChunk


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


def mock_documents(n: int = 3) -> list[RetrievedChunk]:
    """Create a list of mock RetrievedChunk objects."""
    return [
        RetrievedChunk(
            content=f"This is document chunk {i + 1} content.",
            source=f"policy_{i + 1}.md",
        )
        for i in range(n)
    ]

"""
Tests for knowledge base ingestion — document loading, splitting, and storage.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from app.rag.ingest import load_documents, split_documents, KNOWLEDGE_BASE_DIR


class TestLoadDocuments:
    @patch("app.rag.ingest.glob.glob")
    @patch("app.rag.ingest.TextLoader")
    def test_loads_md_files(self, mock_loader_cls, mock_glob):
        mock_glob.return_value = ["/fake/vpn.md", "/fake/leave.md"]
        mock_loader = MagicMock()
        mock_loader.load.side_effect = [
            [Document(page_content="vpn content", metadata={})],
            [Document(page_content="leave content", metadata={})],
        ]
        mock_loader_cls.return_value = mock_loader

        docs = load_documents()

        assert len(docs) == 2
        assert docs[0].metadata["source"] == "vpn.md"
        assert docs[1].metadata["source"] == "leave.md"

    @patch("app.rag.ingest.glob.glob")
    def test_returns_empty_on_no_files(self, mock_glob):
        mock_glob.return_value = []

        docs = load_documents()

        assert docs == []

    @patch("app.rag.ingest.glob.glob")
    @patch("app.rag.ingest.TextLoader")
    def test_handles_load_error_gracefully(self, mock_loader_cls, mock_glob):
        mock_glob.return_value = ["/fake/bad.md"]
        mock_loader = MagicMock()
        mock_loader.load.side_effect = Exception("Corrupt file")
        mock_loader_cls.return_value = mock_loader

        docs = load_documents()

        assert docs == []


class TestSplitDocuments:
    def test_splits_into_chunks(self):
        docs = [Document(page_content="A" * 1000, metadata={})]

        chunks = split_documents(docs)

        assert len(chunks) > 1

    def test_empty_docs_returns_empty(self):
        chunks = split_documents([])
        assert chunks == []


class TestIngest:
    @patch("app.rag.ingest.clear_collection")
    @patch("app.rag.ingest.get_vectorstore")
    @patch("app.rag.ingest.split_documents")
    @patch("app.rag.ingest.load_documents")
    def test_ingest_clears_before_adding(
        self, mock_load, mock_split, mock_vs, mock_clear
    ):
        mock_load.return_value = [Document(page_content="test", metadata={})]
        mock_split.return_value = [Document(page_content="chunk", metadata={})]
        mock_store = MagicMock()
        mock_vs.return_value = mock_store

        from app.rag.ingest import ingest
        ingest()

        mock_clear.assert_called_once()
        mock_store.add_documents.assert_called_once()

    @patch("app.rag.ingest.load_documents")
    def test_ingest_aborts_on_empty(self, mock_load):
        mock_load.return_value = []

        from app.rag.ingest import ingest
        ingest()  # Should not raise

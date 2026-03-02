"""
ChromaDB vector store client.

ChromaDB runs in-process (no separate server needed) with persistence
to disk. This module creates/connects to a persistent ChromaDB collection
and exposes it as a LangChain-compatible vector store for similarity search.

Why ChromaDB?
- Open source, runs locally — no external API key required
- Persistent storage to disk — survives restarts
- LangChain integration via langchain-chroma
- Perfect for prototyping and mid-scale production use
"""

import chromadb
from langchain_chroma import Chroma

from app.config import settings
from app.rag.embeddings import get_embeddings


def get_vectorstore() -> Chroma:
    """
    Create or connect to the persistent ChromaDB vector store.

    Returns:
        A LangChain Chroma instance backed by persistent storage.
    """
    # Create a persistent ChromaDB client
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

    return Chroma(
        client=client,
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embeddings(),
    )


def similarity_search(query: str, k: int = 5) -> list:
    """
    Search the vector store for the most relevant document chunks.

    Args:
        query: The search query text.
        k: Number of top results to return (default: 5).

    Returns:
        List of LangChain Document objects with content and metadata.
    """
    store = get_vectorstore()
    return store.similarity_search(query, k=k)

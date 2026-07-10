"""
ChromaDB vector store — persistent local storage for document embeddings.
"""

import functools
from dataclasses import dataclass

import chromadb
from langchain_chroma import Chroma

from app.config import settings
from app.rag.embeddings import get_embeddings


@dataclass(frozen=True)
class RetrievedChunk:
    """Domain type for a retrieved document chunk."""
    content: str
    source: str


@functools.lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return Chroma(
        client=client,
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embeddings(),
    )


def clear_collection():
    """Delete all documents from the collection. Called before re-ingestion."""
    store = get_vectorstore()
    store.delete_collection()
    # Reset cache so next get_vectorstore() creates a fresh client
    get_vectorstore.cache_clear()


def similarity_search(query: str, k: int = 5) -> list[RetrievedChunk]:
    store = get_vectorstore()
    docs = store.similarity_search(query, k=k)
    return [
        RetrievedChunk(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
        )
        for doc in docs
    ]

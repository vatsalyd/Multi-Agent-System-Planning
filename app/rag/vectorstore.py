"""
Pinecone vector store — cloud vector database for document embeddings.
"""

import functools
from dataclasses import dataclass

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from app.config import settings
from app.rag.embeddings import get_embeddings


@dataclass(frozen=True)
class RetrievedChunk:
    """Domain type for a retrieved document chunk."""
    content: str
    source: str


@functools.lru_cache(maxsize=1)
def get_pinecone_client() -> Pinecone:
    """Get or create Pinecone client (singleton)."""
    return Pinecone(api_key=settings.pinecone_api_key)


def _ensure_index_exists(pc: Pinecone) -> None:
    """Create Pinecone index if it doesn't exist (idempotent)."""
    if settings.pinecone_index_name not in pc.list_indexes().names():
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )


@functools.lru_cache(maxsize=1)
def get_vectorstore() -> PineconeVectorStore:
    pc = get_pinecone_client()
    _ensure_index_exists(pc)
    index = pc.Index(settings.pinecone_index_name)
    return PineconeVectorStore(
        index=index,
        embedding=get_embeddings(),
    )


def clear_collection():
    """Delete all vectors from the index. Called before re-ingestion."""
    pc = get_pinecone_client()
    index = pc.Index(settings.pinecone_index_name)
    index.delete(delete_all=True, namespace="")
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
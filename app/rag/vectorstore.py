"""
Pinecone vector store — cloud vector database for document embeddings.
"""

import functools
import time
from dataclasses import dataclass

from pinecone import Pinecone, ServerlessSpec
from pinecone.core.openapi.shared.exceptions import NotFoundException
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
        # Wait for index to be ready (Pinecone index creation is async)
        for _ in range(60):
            try:
                desc = pc.describe_index(settings.pinecone_index_name)
                if desc.status.ready:
                    break
            except Exception:
                pass
            time.sleep(2)


@functools.lru_cache(maxsize=1)
def get_vectorstore() -> PineconeVectorStore:
    pc = get_pinecone_client()
    _ensure_index_exists(pc)
    # Wait for index to be ready
    for _ in range(30):
        try:
            desc = pc.describe_index(settings.pinecone_index_name)
            if desc.status.ready:
                break
        except Exception:
            pass
        time.sleep(2)
    index = pc.Index(settings.pinecone_index_name)
    return PineconeVectorStore(
        index=index,
        embedding=get_embeddings(),
    )


def clear_collection():
    """Delete all vectors from the index. Called before re-ingestion."""
    pc = get_pinecone_client()
    _ensure_index_exists(pc)
    index = pc.Index(settings.pinecone_index_name)
    try:
        index.delete(delete_all=True, namespace="")
    except NotFoundException:
        pass  # Namespace doesn't exist yet — nothing to clear
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
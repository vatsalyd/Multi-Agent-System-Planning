"""
Pinecone Inference API embeddings — server-side embeddings via Pinecone.
No local model needed. Uses multilingual-e5-large (1024 dims).
"""

import functools

from langchain_pinecone import PineconeEmbeddings

from app.config import settings


@functools.lru_cache(maxsize=1)
def get_embeddings() -> PineconeEmbeddings:
    return PineconeEmbeddings(
        model=settings.pinecone_embedding_model,
        pinecone_api_key=settings.pinecone_api_key,
    )
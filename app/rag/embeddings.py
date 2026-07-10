"""
Local embeddings using HuggingFace sentence-transformers (all-MiniLM-L6-v2).
Runs on CPU, no API key needed.
"""

import functools

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import settings


@functools.lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

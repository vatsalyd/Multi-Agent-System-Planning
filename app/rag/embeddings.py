"""
Free local embeddings using HuggingFace sentence-transformers.

Why sentence-transformers?
- Runs 100% locally on your CPU — no API key, no cost, no internet needed
- all-MiniLM-L6-v2 is a small (80MB), fast model with excellent quality
- Compatible with LangChain's Chroma integration via a thin adapter
"""

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import settings


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return a free, locally-running HuggingFace embedding model.
    The model is downloaded once (~80MB) and cached automatically.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

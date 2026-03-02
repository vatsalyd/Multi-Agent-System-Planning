"""
Embedding utilities for the RAG pipeline.

Wraps OpenAI's embedding model to convert text chunks into vector
representations. These vectors are stored in ChromaDB and used for
semantic similarity search when the Retrieval Agent needs to find
relevant company documentation.

Why text-embedding-3-small?
- It's OpenAI's most cost-effective embedding model
- 1536-dimensional vectors with excellent semantic quality
- ~$0.02 per 1M tokens — very cheap for our knowledge base size
"""

from langchain_openai import OpenAIEmbeddings

from app.config import settings


def get_embeddings() -> OpenAIEmbeddings:
    """
    Create and return an OpenAI embeddings instance.

    Returns:
        OpenAIEmbeddings configured with the model from settings.
    """
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        openai_api_key=settings.openai_api_key,
    )

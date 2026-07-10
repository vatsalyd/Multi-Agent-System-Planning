"""
LLM provider factory — single source of truth for LLM instantiation.
"""

from langchain_groq import ChatGroq

from app.config import settings


def create_llm(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(
        model=settings.groq_model,
        groq_api_key=settings.groq_api_key,
        temperature=temperature,
    )

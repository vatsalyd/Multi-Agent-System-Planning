"""
Centralized application settings.

Uses pydantic-settings to read configuration from environment variables
and .env files. Every module imports settings from here — no hardcoded
API keys or paths anywhere in the codebase.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── OpenAI ──────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"

    # ── ChromaDB ────────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "company_knowledge"

    # ── Server ──────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # ── App metadata ────────────────────────────────────────
    app_name: str = "Multi-Agent Triage System"
    app_version: str = "1.0.0"


# Singleton instance used across the application
settings = Settings()

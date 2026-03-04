"""
Centralized application settings — Groq (free LLM) + local embeddings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "all-MiniLM-L6-v2"

    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "company_knowledge"

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    app_name: str = "Multi-Agent Triage System"
    app_version: str = "1.0.0"


settings = Settings()

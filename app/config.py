"""
Centralized application settings — Groq (free LLM) + Pinecone embeddings + Pinecone vector DB.
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
    groq_request_timeout: int = 30
    groq_max_retries: int = 2

    pinecone_api_key: str = ""
    pinecone_index_name: str = "helixdesk"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_dimension: int = 1024
    pinecone_embedding_model: str = "multilingual-e5-large"

    chunk_size: int = 500
    chunk_overlap: int = 50

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    app_name: str = "Multi-Agent Triage System"
    app_version: str = "1.0.0"


settings = Settings()
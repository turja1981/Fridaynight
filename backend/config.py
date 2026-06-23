from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    anthropic_api_key: str = ""
    jwt_secret: str = "dev-secret-change-in-prod-32chars!!"
    qdrant_path: str = "./data/qdrant"
    active_adapter: str = "insurance_claims"
    log_level: str = "INFO"
    whisper_api_key: str = ""
    # LangSmith
    langchain_tracing_v2: str = "false"
    langchain_api_key: str = ""
    langchain_project: str = "tcs-hackathon-enterprise-ai"
    # Mem0
    mem0_api_key: str = ""
    # Multi-provider LLM support
    openai_api_key: str = ""
    google_api_key: str = ""
    preferred_provider: str = "anthropic"  # anthropic | openai | google

settings = Settings()

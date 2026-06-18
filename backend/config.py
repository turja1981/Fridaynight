from __future__ import annotations
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    anthropic_api_key: str = ""
    jwt_secret: str = "dev-secret-change-in-prod"
    chroma_path: str = "./data/chroma"
    active_adapter: str = "insurance_claims"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()

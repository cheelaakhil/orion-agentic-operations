"""
ORION Backend Configuration

Centralized configuration using pydantic-settings.
Loads from environment variables and .env file.
"""

import os
from typing import Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Application
    app_name: str = "ORION"
    app_version: str = "0.3.0"
    debug: bool = False
    port: int = int(os.getenv("PORT", "8000"))

    # Database
    database_url: str = os.getenv("DATABASE_URL") or os.getenv("ORION_DATABASE_URL") or "postgresql+asyncpg://orion:orion@localhost:5432/orion"
    database_echo: bool = False

    # CORS Origins (accepts list or comma-separated string)
    cors_origins: Union[list[str], str] = [
        "https://orion-agentic-operations-4jim19l0i-cheela-akhils-projects.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    cors_origin_regex: str = r"^https:\/\/.*\.vercel\.app$"

    # Agent Provider
    agent_provider: str = "local"  # "local" | "adya" (adapter-ready)

    # Investigation defaults
    investigation_timeout_seconds: int = 120
    max_hypotheses: int = 5

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[list[str], str]) -> list[str]:
        if isinstance(v, str):
            # Split comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {"env_file": ".env", "env_prefix": "ORION_", "extra": "ignore"}


settings = Settings()


"""
ORION Backend Configuration

Centralized configuration using pydantic-settings.
Loads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Application
    app_name: str = "ORION"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://orion:orion@localhost:5432/orion"
    database_echo: bool = False

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "*",
    ]

    # Agent Provider
    agent_provider: str = "local"  # "local" | "adya" (future)

    # Investigation defaults
    investigation_timeout_seconds: int = 120
    max_hypotheses: int = 5

    model_config = {"env_file": ".env", "env_prefix": "ORION_"}


settings = Settings()

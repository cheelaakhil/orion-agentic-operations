"""
ORION Database Engine and Session Management

Provides both synchronous and asynchronous database engines and session factories.
Supports PostgreSQL (production) and SQLite (testing and offline development).
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import settings

# Determine sync database URL
def get_sync_url() -> str:
    url = os.getenv("DATABASE_URL") or os.getenv("ORION_DATABASE_URL")
    if not url:
        # Default to local verified sqlite db if available for offline dev
        if os.path.exists("orion_verified.db"):
            return "sqlite:///orion_verified.db"
        elif os.path.exists("orion.db"):
            return "sqlite:///orion.db"
        url = settings.database_url

    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return url


# Sync Engine & Session
def create_app_engine():
    sync_url = get_sync_url()
    connect_args = {}
    if sync_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(sync_url, connect_args=connect_args, echo=settings.database_echo)


sync_engine = create_app_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency: yields a synchronous SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

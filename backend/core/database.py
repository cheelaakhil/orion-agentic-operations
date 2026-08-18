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


def init_db_if_needed(engine=None) -> bool:
    """
    Idempotent database initializer for production cloud deployments (e.g. Render Free).
    - Creates tables if they do not exist.
    - Seeds the NovaCart demo dataset if the database is unpopulated.
    - Skips cleanly if data is already present.
    Returns True if seeding occurred, False if skipped.
    """
    eng = engine or sync_engine
    
    # 1. Create tables if not present
    from backend.models.models import Base, Customer, Product
    Base.metadata.create_all(bind=eng)

    # 2. Check if records already exist
    SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    with SessionMaker() as session:
        try:
            prod_count = session.query(Product).count()
            cust_count = session.query(Customer).count()
            if prod_count > 0 and cust_count > 0:
                print(f"[INFO] Database already initialized ({prod_count} products, {cust_count} customers). Skipping seed.")
                return False
        except Exception as e:
            print(f"[WARN] Error checking table counts: {e}")

        # 3. Seed dataset if empty
        print("[*] Unpopulated database detected. Auto-seeding NovaCart dataset for cloud deployment...")
        from data.generate import NovaCartDataGenerator
        generator = NovaCartDataGenerator(session)
        generator.generate_all()
        session.commit()
        print("[✓] NovaCart dataset auto-seeding committed successfully.")
        return True


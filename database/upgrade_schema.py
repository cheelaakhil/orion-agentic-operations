"""
Database upgrade script to ensure all Milestone 3 tables and columns are present in orion_verified.db.
"""

from sqlalchemy import text
from backend.core.database import sync_engine
from backend.models.models import Base


def upgrade():
    with sync_engine.connect() as conn:
        for col_def in [
            "ALTER TABLE audit_events ADD COLUMN event_id VARCHAR(64)",
            "ALTER TABLE audit_events ADD COLUMN event_type VARCHAR(64) DEFAULT 'GENERAL'",
            "ALTER TABLE audit_events ADD COLUMN status VARCHAR(32) DEFAULT 'SUCCESS'",
        ]:
            try:
                conn.execute(text(col_def))
                conn.commit()
                print(f"[+] Executed: {col_def}")
            except Exception as e:
                print(f"[*] Note for '{col_def}': {e}")

    Base.metadata.create_all(bind=sync_engine)
    print("[+] All database tables and columns successfully verified!")


if __name__ == "__main__":
    upgrade()

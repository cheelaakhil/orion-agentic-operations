"""
Unit tests for automatic idempotent database initialization.
"""

import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import init_db_if_needed
from backend.models.models import Customer, Product


def test_init_db_if_needed_idempotent():
    # Use a temporary SQLite database file to test across connections
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        engine = create_engine(f"sqlite:///{tmp_path}", connect_args={"check_same_thread": False})
        
        # 1. First call on empty database -> seeds records
        seeded_first = init_db_if_needed(engine)
        assert seeded_first is True, "Expected first call to seed empty database"

        # Verify records exist
        Session = sessionmaker(bind=engine)
        with Session() as session:
            prod_count = session.query(Product).count()
            cust_count = session.query(Customer).count()
            assert prod_count > 0, f"Expected products to be seeded, found {prod_count}"
            assert cust_count > 0, f"Expected customers to be seeded, found {cust_count}"

        # 2. Second call on existing database -> skips seeding
        seeded_second = init_db_if_needed(engine)
        assert seeded_second is False, "Expected second call to skip already initialized database"
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

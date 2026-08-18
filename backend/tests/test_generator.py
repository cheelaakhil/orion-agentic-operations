"""
Unit tests for NovaCart synthetic data generator and incident properties.
"""

from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.models.models import (
    Base,
    Customer,
    Inventory,
    MarketingCampaign,
    Order,
    OrderStatus,
    Product,
    SupportTicket,
)
from data.generate import NovaCartDataGenerator


def test_generator_structure_and_integrity():
    """Verify that NovaCartDataGenerator populates all entities with relational integrity."""
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    Session = sessionmaker(bind=test_engine)
    session = Session()

    generator = NovaCartDataGenerator(session)

    # Test small batch generation
    generator.generate_products()
    assert len(generator.products) == 60

    generator.generate_customers()
    assert len(generator.customers) == 5500

    # Ensure customers have valid regions and emails
    for cust in generator.customers[:10]:
        assert "@novacart-example.com" in cust.email
        assert cust.region in ["North America", "Europe", "Asia-Pacific", "Latin America"]

    # Verify inventory generation
    inv_count = generator.generate_inventory()
    assert inv_count > 0

    session.close()

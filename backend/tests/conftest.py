"""
Pytest configuration and test database fixtures for ORION.
"""

from datetime import datetime, timedelta
from decimal import Decimal
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from backend.models.models import (
    Base,
    Customer,
    CustomerSegment,
    Inventory,
    MarketingCampaign,
    Order,
    OrderStatus,
    Product,
    SupportTicket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


@pytest.fixture(scope="session")
def engine():
    """Create in-memory SQLite database with StaticPool for testing."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=test_engine)
    return test_engine


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a transactional database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def populated_db(db_session: Session):
    """Populate a structured 60-day dataset with known baseline and incident dynamics."""
    # 1. Products
    p1 = Product(
        product_id="PROD-001",
        name="Wireless Noise-Canceling Headphones",
        category="Electronics",
        sku="SKU-ELEC-001",
        unit_cost=Decimal("60.00"),
        list_price=Decimal("120.00"),
        status="ACTIVE",
    )
    p2 = Product(
        product_id="PROD-002",
        name="Stainless Steel Chef Knife",
        category="Home & Kitchen",
        sku="SKU-HOME-002",
        unit_cost=Decimal("25.00"),
        list_price=Decimal("50.00"),
        status="ACTIVE",
    )
    p3 = Product(
        product_id="PROD-003",
        name="Organic Cotton T-Shirt",
        category="Apparel",
        sku="SKU-APP-003",
        unit_cost=Decimal("10.00"),
        list_price=Decimal("25.00"),
        status="ACTIVE",
    )
    db_session.add_all([p1, p2, p3])
    db_session.flush()

    # 2. Customers
    c1 = Customer(
        customer_id="CUST-001",
        name="Alice Johnson",
        email="alice@example.com",
        segment=CustomerSegment.VIP.value,
        region="North America",
        created_at=datetime(2026, 5, 1),
    )
    c2 = Customer(
        customer_id="CUST-002",
        name="Bob Smith",
        email="bob@example.com",
        segment=CustomerSegment.REGULAR.value,
        region="Europe",
        created_at=datetime(2026, 5, 5),
    )
    c3 = Customer(
        customer_id="CUST-003",
        name="Charlie Brown",
        email="charlie@example.com",
        segment=CustomerSegment.AT_RISK.value,
        region="Asia-Pacific",
        created_at=datetime(2026, 5, 10),
    )
    db_session.add_all([c1, c2, c3])
    db_session.flush()

    # 3. Orders: Baseline (May 1 - May 31) vs Incident (June 1 - June 30)
    # Baseline orders: High volume, repeat buyers
    orders = [
        # Baseline
        Order(order_id="ORD-001", customer_id=c1.id, product_id=p1.id, region="North America", quantity=1, unit_price=Decimal("120.00"), total_amount=Decimal("120.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 5, 2)),
        Order(order_id="ORD-002", customer_id=c1.id, product_id=p2.id, region="North America", quantity=2, unit_price=Decimal("50.00"), total_amount=Decimal("100.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 5, 15)),  # repeat
        Order(order_id="ORD-003", customer_id=c2.id, product_id=p2.id, region="Europe", quantity=1, unit_price=Decimal("50.00"), total_amount=Decimal("50.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 5, 10)),
        Order(order_id="ORD-004", customer_id=c2.id, product_id=p3.id, region="Europe", quantity=2, unit_price=Decimal("25.00"), total_amount=Decimal("50.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 5, 20)),  # repeat
        Order(order_id="ORD-005", customer_id=c3.id, product_id=p3.id, region="Asia-Pacific", quantity=1, unit_price=Decimal("25.00"), total_amount=Decimal("25.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 5, 25)),
        # Incident: Lower volume, fewer repeats, some cancellations
        Order(order_id="ORD-006", customer_id=c1.id, product_id=p3.id, region="North America", quantity=1, unit_price=Decimal("25.00"), total_amount=Decimal("25.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 6, 5)),
        Order(order_id="ORD-007", customer_id=c2.id, product_id=p2.id, region="Europe", quantity=1, unit_price=Decimal("50.00"), total_amount=Decimal("50.00"), status=OrderStatus.COMPLETED.value, order_date=datetime(2026, 6, 12)),
        Order(order_id="ORD-008", customer_id=c3.id, product_id=p1.id, region="Asia-Pacific", quantity=1, unit_price=Decimal("120.00"), total_amount=Decimal("120.00"), status=OrderStatus.CANCELLED.value, order_date=datetime(2026, 6, 18)),
    ]
    db_session.add_all(orders)
    db_session.flush()

    # 4. Inventory: Stockout in Electronics in June
    inv = [
        Inventory(product_id=p1.id, warehouse_region="North America", quantity_on_hand=50, reorder_point=20, stockout_flag=False, snapshot_date=datetime(2026, 5, 15)),
        Inventory(product_id=p1.id, warehouse_region="North America", quantity_on_hand=0, reorder_point=20, stockout_flag=True, snapshot_date=datetime(2026, 6, 15)),
        Inventory(product_id=p2.id, warehouse_region="Europe", quantity_on_hand=40, reorder_point=20, stockout_flag=False, snapshot_date=datetime(2026, 5, 15)),
        Inventory(product_id=p2.id, warehouse_region="Europe", quantity_on_hand=30, reorder_point=20, stockout_flag=False, snapshot_date=datetime(2026, 6, 15)),
        Inventory(product_id=p3.id, warehouse_region="Asia-Pacific", quantity_on_hand=100, reorder_point=20, stockout_flag=False, snapshot_date=datetime(2026, 5, 15)),
        Inventory(product_id=p3.id, warehouse_region="Asia-Pacific", quantity_on_hand=80, reorder_point=20, stockout_flag=False, snapshot_date=datetime(2026, 6, 15)),
    ]
    db_session.add_all(inv)
    db_session.flush()

    # 5. Support Tickets: Quick resolution in May, long breach in June
    tickets = [
        SupportTicket(ticket_id="TCK-001", customer_id=c1.id, category=TicketCategory.GENERAL.value, priority=TicketPriority.LOW.value, status=TicketStatus.RESOLVED.value, region="North America", created_at=datetime(2026, 5, 3), resolution_time_hours=1.5, sla_breached=False, satisfaction_score=5),
        SupportTicket(ticket_id="TCK-002", customer_id=c2.id, category=TicketCategory.DELIVERY.value, priority=TicketPriority.MEDIUM.value, status=TicketStatus.RESOLVED.value, region="Europe", created_at=datetime(2026, 5, 12), resolution_time_hours=2.0, sla_breached=False, satisfaction_score=4),
        SupportTicket(ticket_id="TCK-003", customer_id=c1.id, category=TicketCategory.STOCK_INQUIRY.value, priority=TicketPriority.HIGH.value, status=TicketStatus.RESOLVED.value, region="North America", created_at=datetime(2026, 6, 10), resolution_time_hours=32.0, sla_breached=True, satisfaction_score=1),
        SupportTicket(ticket_id="TCK-004", customer_id=c3.id, category=TicketCategory.DELIVERY.value, priority=TicketPriority.URGENT.value, status=TicketStatus.RESOLVED.value, region="Asia-Pacific", created_at=datetime(2026, 6, 20), resolution_time_hours=28.5, sla_breached=True, satisfaction_score=1),
    ]
    db_session.add_all(tickets)
    db_session.flush()

    # 6. Marketing Campaigns
    camps = [
        MarketingCampaign(campaign_id="CAMP-001", name="May Spring Sale", channel="Paid Social", region="North America", start_date=datetime(2026, 5, 1), end_date=datetime(2026, 5, 20), budget=Decimal("1000.00"), spend=Decimal("1000.00"), impressions=50000, clicks=2000, conversions=100, attributed_revenue=Decimal("5000.00")),
        MarketingCampaign(campaign_id="CAMP-002", name="June Summer Promo", channel="Search", region="North America", start_date=datetime(2026, 6, 1), end_date=datetime(2026, 6, 20), budget=Decimal("1000.00"), spend=Decimal("1000.00"), impressions=45000, clicks=1800, conversions=35, attributed_revenue=Decimal("1750.00")),
    ]
    db_session.add_all(camps)
    db_session.commit()

    return db_session

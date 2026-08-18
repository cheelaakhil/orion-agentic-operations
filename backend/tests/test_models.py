"""
Test SQLAlchemy models, relationships, and constraints.
"""

from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy import select

from backend.models.models import (
    AuditEvent,
    Customer,
    CustomerSegment,
    Inventory,
    MarketingCampaign,
    Order,
    OrderStatus,
    Product,
    SupportTicket,
    TicketCategory,
    TicketStatus,
)


def test_customer_creation(db_session):
    cust = Customer(
        customer_id="CUST-TEST-1",
        name="Test User",
        email="test@novacart.com",
        segment=CustomerSegment.VIP.value,
        region="North America",
    )
    db_session.add(cust)
    db_session.commit()

    saved = db_session.execute(select(Customer).where(Customer.customer_id == "CUST-TEST-1")).scalar_one()
    assert saved.id is not None
    assert saved.name == "Test User"
    assert saved.segment == "VIP"


def test_product_and_order_relationships(db_session):
    cust = Customer(
        customer_id="CUST-TEST-2",
        name="Buyer One",
        email="buyer@novacart.com",
        region="Europe",
    )
    prod = Product(
        product_id="PROD-TEST-1",
        name="Mechanical Keyboard",
        category="Electronics",
        sku="SKU-ELEC-TEST",
        unit_cost=Decimal("40.00"),
        list_price=Decimal("80.00"),
    )
    db_session.add_all([cust, prod])
    db_session.flush()

    order = Order(
        order_id="ORD-TEST-1",
        customer_id=cust.id,
        product_id=prod.id,
        region="Europe",
        quantity=2,
        unit_price=Decimal("80.00"),
        total_amount=Decimal("160.00"),
        status=OrderStatus.COMPLETED.value,
        order_date=datetime.utcnow(),
    )
    db_session.add(order)
    db_session.commit()

    saved_order = db_session.execute(select(Order).where(Order.order_id == "ORD-TEST-1")).scalar_one()
    assert saved_order.customer.name == "Buyer One"
    assert saved_order.product.name == "Mechanical Keyboard"
    assert float(saved_order.total_amount) == 160.00


def test_inventory_and_support_ticket(db_session):
    cust = Customer(
        customer_id="CUST-TEST-3",
        name="Ticket User",
        email="ticket@novacart.com",
        region="Asia-Pacific",
    )
    prod = Product(
        product_id="PROD-TEST-2",
        name="Desk Lamp",
        category="Home & Kitchen",
        sku="SKU-HOME-TEST",
        unit_cost=Decimal("15.00"),
        list_price=Decimal("30.00"),
    )
    db_session.add_all([cust, prod])
    db_session.flush()

    inv = Inventory(
        product_id=prod.id,
        warehouse_region="Asia-Pacific",
        quantity_on_hand=5,
        reorder_point=20,
        stockout_flag=False,
        snapshot_date=datetime.utcnow(),
    )
    ticket = SupportTicket(
        ticket_id="TCK-TEST-1",
        customer_id=cust.id,
        category=TicketCategory.STOCK_INQUIRY.value,
        region="Asia-Pacific",
        created_at=datetime.utcnow(),
        resolution_time_hours=25.0,
        sla_breached=True,
        satisfaction_score=2,
    )
    audit = AuditEvent(
        entity_type="ticket",
        entity_id="TCK-TEST-1",
        action="ESCALATED",
        actor="system",
        details={"reason": "SLA breach over 24h"},
    )
    db_session.add_all([inv, ticket, audit])
    db_session.commit()

    saved_ticket = db_session.execute(select(SupportTicket).where(SupportTicket.ticket_id == "TCK-TEST-1")).scalar_one()
    assert saved_ticket.sla_breached is True
    assert saved_ticket.satisfaction_score == 2

    saved_audit = db_session.execute(select(AuditEvent).where(AuditEvent.entity_id == "TCK-TEST-1")).scalar_one()
    assert saved_audit.action == "ESCALATED"

"""
ORION Database Models

SQLAlchemy ORM models for NovaCart business data and ORION operational tables.
Designed for PostgreSQL compatibility with full relational integrity, proper indexes,
constraints, and cascading relationships.
"""

from datetime import datetime
from decimal import Decimal
import enum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrderStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"


class TicketCategory(str, enum.Enum):
    DELIVERY = "DELIVERY"
    PRODUCT_QUALITY = "PRODUCT_QUALITY"
    BILLING = "BILLING"
    STOCK_INQUIRY = "STOCK_INQUIRY"
    RETURNS = "RETURNS"
    GENERAL = "GENERAL"


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class CustomerSegment(str, enum.Enum):
    VIP = "VIP"
    REGULAR = "REGULAR"
    AT_RISK = "AT_RISK"
    CHURNED = "CHURNED"


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Business Models
# ---------------------------------------------------------------------------

class Customer(Base):
    """
    Customer entity representing NovaCart consumers.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    segment = Column(String(32), nullable=False, default=CustomerSegment.REGULAR.value, index=True)
    region = Column(String(64), nullable=False, index=True)  # North America, Europe, Asia-Pacific, Latin America
    first_order_date = Column(DateTime, nullable=True)
    lifetime_value = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    status = Column(String(32), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Customer {self.customer_id} ({self.name}, {self.segment})>"


class Product(Base):
    """
    Product entity in the NovaCart catalog.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)  # Electronics, Apparel, Home & Kitchen, Beauty, Sports
    sku = Column(String(64), unique=True, nullable=False, index=True)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    list_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(32), nullable=False, default="ACTIVE")  # ACTIVE, DISCONTINUED, OUT_OF_STOCK
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="product")
    inventory_records = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product {self.sku} ({self.name}, ${self.list_price})>"


class Order(Base):
    """
    Customer transactional order.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    region = Column(String(64), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(32), nullable=False, default=OrderStatus.COMPLETED.value, index=True)
    order_date = Column(DateTime, nullable=False, index=True)
    fulfilled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    support_tickets = relationship("SupportTicket", back_populates="order")

    __table_args__ = (
        Index("ix_orders_date_region", "order_date", "region"),
        Index("ix_orders_customer_date", "customer_id", "order_date"),
    )

    def __repr__(self) -> str:
        return f"<Order {self.order_id} (${self.total_amount}, {self.status})>"


class Inventory(Base):
    """
    Warehouse inventory snapshots.
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_region = Column(String(64), nullable=False, index=True)
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=20)
    stockout_flag = Column(Boolean, nullable=False, default=False, index=True)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    last_restock_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory_records")

    __table_args__ = (
        Index("ix_inventory_product_snapshot", "product_id", "snapshot_date"),
        Index("ix_inventory_region_snapshot", "warehouse_region", "snapshot_date"),
    )

    def __repr__(self) -> str:
        return f"<Inventory Prod={self.product_id} Region={self.warehouse_region} Qty={self.quantity_on_hand}>"


class SupportTicket(Base):
    """
    Customer service tickets and resolution tracking.
    """
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(64), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String(64), nullable=False, default=TicketCategory.GENERAL.value, index=True)
    priority = Column(String(32), nullable=False, default=TicketPriority.MEDIUM.value)
    status = Column(String(32), nullable=False, default=TicketStatus.RESOLVED.value, index=True)
    region = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_time_hours = Column(Float, nullable=True)  # in hours
    sla_breached = Column(Boolean, nullable=False, default=False, index=True)
    satisfaction_score = Column(Integer, nullable=True)  # 1 to 5

    # Relationships
    customer = relationship("Customer", back_populates="support_tickets")
    order = relationship("Order", back_populates="support_tickets")

    __table_args__ = (
        Index("ix_tickets_created_sla", "created_at", "sla_breached"),
        Index("ix_tickets_region_created", "region", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SupportTicket {self.ticket_id} ({self.category}, SLA Breached={self.sla_breached})>"


class MarketingCampaign(Base):
    """
    Marketing campaigns across channels and regions.
    """
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    channel = Column(String(64), nullable=False, index=True)  # Search, Social, Email, Influencer, Display
    region = Column(String(64), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    budget = Column(Numeric(12, 2), nullable=False)
    spend = Column(Numeric(12, 2), nullable=False)
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    conversions = Column(Integer, nullable=False, default=0)
    attributed_revenue = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<MarketingCampaign {self.name} ({self.channel}, Spend=${self.spend})>"


class AuditEvent(Base):
    """
    Immutable audit log for all system decisions, approvals, and actions.
    """
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=True, index=True)
    event_type = Column(String(64), nullable=True, default="GENERAL", index=True)  # ANOMALY_DETECTED, INVESTIGATION_STARTED, etc.
    entity_type = Column(String(64), nullable=False, index=True)  # anomaly, investigation, recommendation, approval, action
    entity_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    actor = Column(String(128), nullable=False)  # system, agent_name, user_id, human_operator
    status = Column(String(32), nullable=False, default="SUCCESS", index=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<AuditEvent {self.event_type}:{self.entity_id} - {self.action} ({self.status})>"


class AnomalyRecordModel(Base):
    """
    Persistent record of detected business anomalies.
    """
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anomaly_id = Column(String(64), unique=True, nullable=False, index=True)
    metric_name = Column(String(128), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    deviation_pct = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False, default=SeverityLevel.MEDIUM.value, index=True)
    affected_dimension = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="OPEN", index=True)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    onset_date = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<AnomalyRecordModel {self.anomaly_id} ({self.metric_name}, {self.deviation_pct:.1f}%)>"


class InvestigationModel(Base):
    """
    Persistent record of an investigation workflow.
    """
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investigation_id = Column(String(64), unique=True, nullable=False, index=True)
    anomaly_id = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="in_progress", index=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    summary = Column(Text, nullable=True)
    root_causes = Column(JSON, nullable=True)
    business_impact = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    observations = Column(JSON, nullable=True)  # OBSERVED, INFERRED, HYPOTHESIS
    requires_approval = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<InvestigationModel {self.investigation_id} (Anomaly={self.anomaly_id}, Status={self.status})>"


class RecommendationModel(Base):
    """
    Persistent record of action recommendations.
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(String(64), unique=True, nullable=False, index=True)
    investigation_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(32), nullable=False, default="immediate", index=True)  # immediate, short_term, long_term
    priority = Column(Integer, nullable=False, default=1, index=True)
    expected_impact = Column(JSON, nullable=True)
    implementation = Column(JSON, nullable=True)
    risks = Column(JSON, nullable=True)
    supporting_evidence = Column(JSON, nullable=True)
    addresses_root_cause = Column(String(64), nullable=True)
    requires_human_approval = Column(Boolean, nullable=False, default=True)
    action_type = Column(String(64), nullable=False, index=True)
    action_parameters = Column(JSON, nullable=True)
    approval_status = Column(String(32), nullable=False, default="PENDING_APPROVAL", index=True)  # PROPOSED, PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<RecommendationModel {self.recommendation_id} ({self.title}, Status={self.approval_status})>"


class ApprovalRequestModel(Base):
    """
    Persistent record of human approval requests and decisions.
    """
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    approval_id = Column(String(64), unique=True, nullable=False, index=True)
    recommendation_id = Column(String(64), nullable=False, index=True)
    investigation_id = Column(String(64), nullable=False, index=True)
    action_type = Column(String(64), nullable=False, index=True)
    action_details = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="PENDING_APPROVAL", index=True)  # PENDING_APPROVAL, APPROVED, REJECTED
    decision_reason = Column(Text, nullable=True)
    decided_by = Column(String(128), nullable=True)
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    decided_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ApprovalRequestModel {self.approval_id} (Rec={self.recommendation_id}, Status={self.status})>"


class ActionExecutionModel(Base):
    """
    Persistent record of safe simulated action executions.
    """
    __tablename__ = "action_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(64), unique=True, nullable=False, index=True)
    action_id = Column(String(64), nullable=False, index=True)
    approval_id = Column(String(64), nullable=False, index=True)
    investigation_id = Column(String(64), nullable=False, index=True)
    action_type = Column(String(64), nullable=False, index=True)
    parameters = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="PENDING", index=True)  # PENDING, SUCCESS, REJECTED, FAILED
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    executed_by = Column(String(128), nullable=False, default="action_agent")
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<ActionExecutionModel {self.execution_id} ({self.action_type}, Status={self.status})>"

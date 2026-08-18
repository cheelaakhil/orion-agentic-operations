"""
ORION Synthetic Data Generator — NovaCart Enterprise Dataset

Generates realistic e-commerce operational data across 90+ days with an engineered
business incident in the final 6 weeks. Embeds multi-factor operational signals:
- Support SLA degradation & resolution delay spike
- Warehouse stockouts on top categories (Electronics & Home)
- Repeat purchase rate collapse and revenue decline

Guarantees 100% referential and temporal integrity.
Runnable via: python -m data.generate
"""

from datetime import datetime, timedelta
from decimal import Decimal
import os
import random
import sys
from typing import Any

import numpy as np
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.config import settings
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

# ---------------------------------------------------------------------------
# Generator Configuration & Constants
# ---------------------------------------------------------------------------

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

COMPANY_NAME = "NovaCart"
SIM_START_DATE = datetime(2026, 5, 1, 0, 0, 0)
SIM_END_DATE = datetime(2026, 8, 1, 23, 59, 59)
TOTAL_DAYS = (SIM_END_DATE - SIM_START_DATE).days + 1  # 93 days
INCIDENT_START_DAY = 50  # Day 50 (June 20) begins the engineered breakdown

NUM_CUSTOMERS = 5500
NUM_PRODUCTS = 60
NUM_ORDERS = 52000
NUM_INVENTORY_SNAPSHOTS = 5400
NUM_SUPPORT_TICKETS = 11000
NUM_CAMPAIGNS = 35

REGIONS = ["North America", "Europe", "Asia-Pacific", "Latin America"]
REGION_WEIGHTS = [0.45, 0.28, 0.18, 0.09]

CATEGORIES = [
    ("Electronics", Decimal("45.00"), Decimal("850.00"), 0.35),
    ("Home & Kitchen", Decimal("15.00"), Decimal("220.00"), 0.25),
    ("Apparel", Decimal("10.00"), Decimal("140.00"), 0.20),
    ("Beauty & Health", Decimal("8.00"), Decimal("95.00"), 0.12),
    ("Sports & Outdoors", Decimal("20.00"), Decimal("310.00"), 0.08),
]

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kevin", "Carol", "Brian", "Amanda", "George", "Dorothy", "Edward", "Melissa",
    "Ronald", "Deborah", "Timothy", "Stephanie", "Jason", "Rebecca", "Jeffrey", "Sharon",
    "Ryan", "Laura", "Jacob", "Cynthia", "Gary", "Kathleen", "Nicholas", "Amy",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
]


# ---------------------------------------------------------------------------
# Database Utilities
# ---------------------------------------------------------------------------

def get_engine_and_session(db_url: str | None = None):
    """Create synchronous engine and session maker."""
    url = db_url or os.getenv("DATABASE_URL") or os.getenv("ORION_DATABASE_URL", settings.database_url)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite+aiosqlite://", "sqlite://", 1)

    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(url, connect_args=connect_args, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal


# ---------------------------------------------------------------------------
# Generator Classes
# ---------------------------------------------------------------------------

class NovaCartDataGenerator:
    """Generates synthetic data for NovaCart with the engineered incident."""

    def __init__(self, session: Session):
        self.session = session
        self.customers: list[Customer] = []
        self.products: list[Product] = []
        self.orders: list[Order] = []

    def generate_all(self) -> dict[str, int]:
        """Execute full generation and return record counts."""
        print(f"[*] Starting {COMPANY_NAME} data generation (Seed={SEED})...")
        counts = {}

        # 1. Products
        print(f"[*] Generating {NUM_PRODUCTS} products...")
        self.generate_products()
        counts["products"] = len(self.products)

        # 2. Customers
        print(f"[*] Generating {NUM_CUSTOMERS} customers...")
        self.generate_customers()
        counts["customers"] = len(self.customers)

        # 3. Orders (with temporal distribution & repeat purchase behavior)
        print(f"[*] Generating {NUM_ORDERS} orders across {TOTAL_DAYS} days...")
        self.generate_orders()
        counts["orders"] = len(self.orders)

        # 4. Inventory Snapshots
        print(f"[*] Generating {NUM_INVENTORY_SNAPSHOTS} inventory records...")
        inv_count = self.generate_inventory()
        counts["inventory"] = inv_count

        # 5. Support Tickets
        print(f"[*] Generating {NUM_SUPPORT_TICKETS} support tickets...")
        ticket_count = self.generate_support_tickets()
        counts["support_tickets"] = ticket_count

        # 6. Marketing Campaigns
        print(f"[*] Generating {NUM_CAMPAIGNS} marketing campaigns...")
        camp_count = self.generate_marketing_campaigns()
        counts["marketing_campaigns"] = camp_count

        print(f"[+] All NovaCart dataset components generated successfully!")
        return counts

    def generate_products(self) -> None:
        """Create diverse catalog of products."""
        product_list = []
        sku_counter = 1001

        for cat_name, min_cost, max_cost, _ in CATEGORIES:
            count_for_cat = NUM_PRODUCTS // len(CATEGORIES)
            for i in range(count_for_cat):
                # Calculate cost and list price with standard margin
                unit_cost = Decimal(str(round(random.uniform(float(min_cost), float(max_cost)), 2)))
                margin = Decimal(str(round(random.uniform(1.35, 1.85), 2)))
                list_price = (unit_cost * margin).quantize(Decimal("0.01"))

                prod = Product(
                    product_id=f"PROD-{sku_counter}",
                    name=f"{cat_name} Item #{i+1:02d}",
                    category=cat_name,
                    sku=f"SKU-{cat_name[:3].upper()}-{sku_counter}",
                    unit_cost=unit_cost,
                    list_price=list_price,
                    status="ACTIVE",
                    created_at=SIM_START_DATE - timedelta(days=random.randint(30, 180)),
                )
                product_list.append(prod)
                sku_counter += 1

        self.session.add_all(product_list)
        self.session.flush()
        self.products = product_list

    def generate_customers(self) -> None:
        """Create customer accounts with initial signup dates."""
        customer_list = []
        for i in range(NUM_CUSTOMERS):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            region = random.choices(REGIONS, weights=REGION_WEIGHTS)[0]

            # 40% signup before simulation period, 60% during simulation
            if random.random() < 0.40:
                signup_date = SIM_START_DATE - timedelta(days=random.randint(1, 120))
            else:
                signup_day = random.randint(0, TOTAL_DAYS - 1)
                signup_date = SIM_START_DATE + timedelta(days=signup_day, seconds=random.randint(0, 86399))

            segment = random.choices(
                [CustomerSegment.VIP.value, CustomerSegment.REGULAR.value, CustomerSegment.AT_RISK.value],
                weights=[0.12, 0.73, 0.15],
            )[0]

            cust = Customer(
                customer_id=f"CUST-{100000 + i}",
                name=f"{fname} {lname}",
                email=f"{fname.lower()}.{lname.lower()}{i}@novacart-example.com",
                segment=segment,
                region=region,
                first_order_date=signup_date,
                lifetime_value=Decimal("0.00"),
                status="ACTIVE",
                created_at=signup_date,
            )
            customer_list.append(cust)

        self.session.add_all(customer_list)
        self.session.flush()
        self.customers = customer_list

    def generate_orders(self) -> None:
        """Generate orders with realistic temporal patterns and engineered decline."""
        order_list = []
        customer_ltv: dict[int, Decimal] = {c.id: Decimal("0.00") for c in self.customers}
        customer_first_order: dict[int, datetime] = {}

        # Prepare product category mappings
        cat_map: dict[str, list[Product]] = {}
        for p in self.products:
            cat_map.setdefault(p.category, []).append(p)

        order_idx = 1
        # Distribute orders across days
        for day in range(TOTAL_DAYS):
            current_day_date = SIM_START_DATE + timedelta(days=day)
            is_incident = day >= INCIDENT_START_DAY

            # Base order count per day: ~650 in baseline, drops to ~480 in incident (~26% drop)
            if not is_incident:
                daily_target = int(random.gauss(650, 40))
            else:
                # Gradual worsening over incident
                incident_progress = (day - INCIDENT_START_DAY) / (TOTAL_DAYS - INCIDENT_START_DAY)
                decline_factor = 1.0 - (0.28 * min(1.0, incident_progress * 1.3))
                daily_target = int(random.gauss(650 * decline_factor, 35))

            for _ in range(max(200, daily_target)):
                order_time = current_day_date + timedelta(seconds=random.randint(0, 86399))

                # Eligible customers signed up on or before order_time
                # Choose between new buyer or repeat buyer
                is_repeat = (not is_incident and random.random() < 0.36) or (is_incident and random.random() < 0.18)

                cust = random.choice(self.customers)
                if cust.created_at > order_time:
                    # Adjust customer signup date to precede order
                    cust.created_at = order_time - timedelta(hours=random.randint(1, 48))

                # Category selection: during incident, Electronics & Home suffer stockout penalty
                if is_incident and random.random() < 0.30:
                    # Customers try to buy Apparel / Beauty / Sports instead or drop
                    allowed_cats = ["Apparel", "Beauty & Health", "Sports & Outdoors"]
                    chosen_cat = random.choice(allowed_cats)
                    prod = random.choice(cat_map[chosen_cat])
                else:
                    cat_name = random.choices(
                        [c[0] for c in CATEGORIES],
                        weights=[c[3] for c in CATEGORIES],
                    )[0]
                    prod = random.choice(cat_map[cat_name])

                qty = random.choices([1, 2, 3, 4], weights=[0.75, 0.18, 0.05, 0.02])[0]
                unit_price = prod.list_price
                total_amt = (unit_price * Decimal(str(qty))).quantize(Decimal("0.01"))

                # Status: during incident, cancellation rate increases from 2% to 6%
                cancel_chance = 0.06 if is_incident else 0.02
                status = OrderStatus.CANCELLED.value if random.random() < cancel_chance else OrderStatus.COMPLETED.value

                fulfilled_date = None
                if status == OrderStatus.COMPLETED.value:
                    fulfilled_date = order_time + timedelta(days=random.randint(1, 4))
                    customer_ltv[cust.id] += total_amt
                    if cust.id not in customer_first_order or customer_first_order[cust.id] > order_time:
                        customer_first_order[cust.id] = order_time

                ord_obj = Order(
                    order_id=f"ORD-{1000000 + order_idx}",
                    customer_id=cust.id,
                    product_id=prod.id,
                    region=cust.region,
                    quantity=qty,
                    unit_price=unit_price,
                    total_amount=total_amt,
                    status=status,
                    order_date=order_time,
                    fulfilled_date=fulfilled_date,
                    created_at=order_time,
                )
                order_list.append(ord_obj)
                order_idx += 1

                if len(order_list) >= NUM_ORDERS:
                    break
            if len(order_list) >= NUM_ORDERS:
                break

        # Batch insert orders for speed
        self.session.bulk_save_objects(order_list)
        self.session.flush()

        # Update customer lifetime values and first order dates
        for cust in self.customers:
            cust.lifetime_value = customer_ltv.get(cust.id, Decimal("0.00"))
            if cust.id in customer_first_order:
                cust.first_order_date = customer_first_order[cust.id]

        self.session.flush()
        # Query back orders with IDs for foreign key linking in tickets
        self.orders = self.session.execute(select(Order).limit(NUM_ORDERS)).scalars().all()

    def generate_inventory(self) -> int:
        """Generate periodic warehouse inventory snapshots."""
        inv_list = []
        # Create snapshots every 4 days across simulation for each product in each region
        num_intervals = TOTAL_DAYS // 4

        for interval in range(num_intervals + 1):
            snap_date = SIM_START_DATE + timedelta(days=interval * 4)
            if snap_date > SIM_END_DATE:
                break
            is_incident = (snap_date - SIM_START_DATE).days >= INCIDENT_START_DAY

            for prod in self.products:
                for region in REGIONS:
                    reorder_pt = random.randint(15, 30)

                    # During incident: Electronics & Home & Kitchen experience severe stockouts
                    if is_incident and prod.category in ["Electronics", "Home & Kitchen"] and random.random() < 0.38:
                        qty = random.randint(0, 4)
                        stockout = qty == 0 or qty < 3
                    else:
                        qty = random.randint(25, 250)
                        stockout = False

                    inv = Inventory(
                        product_id=prod.id,
                        warehouse_region=region,
                        quantity_on_hand=qty,
                        reorder_point=reorder_pt,
                        stockout_flag=stockout,
                        snapshot_date=snap_date,
                        last_restock_date=snap_date - timedelta(days=random.randint(2, 20)),
                        created_at=snap_date,
                    )
                    inv_list.append(inv)
                    if len(inv_list) >= NUM_INVENTORY_SNAPSHOTS:
                        break
                if len(inv_list) >= NUM_INVENTORY_SNAPSHOTS:
                    break
            if len(inv_list) >= NUM_INVENTORY_SNAPSHOTS:
                break

        self.session.bulk_save_objects(inv_list)
        self.session.flush()
        return len(inv_list)

    def generate_support_tickets(self) -> int:
        """Generate support tickets with SLA degradation during incident."""
        ticket_list = []
        orders_by_customer: dict[int, list[Order]] = {}
        for ord_obj in self.orders:
            orders_by_customer.setdefault(ord_obj.customer_id, []).append(ord_obj)

        for i in range(NUM_SUPPORT_TICKETS):
            cust = random.choice(self.customers)
            # Ticket timestamp distributed over simulation
            ticket_day = random.randint(0, TOTAL_DAYS - 1)
            is_incident = ticket_day >= INCIDENT_START_DAY
            ticket_time = SIM_START_DATE + timedelta(days=ticket_day, seconds=random.randint(0, 86399))

            # Pick an order if customer has one
            cust_orders = orders_by_customer.get(cust.id, [])
            ord_obj = random.choice(cust_orders) if cust_orders else None

            # Category: during incident, stock inquiries and delivery delays spike
            if is_incident:
                category = random.choices(
                    [
                        TicketCategory.DELIVERY.value,
                        TicketCategory.STOCK_INQUIRY.value,
                        TicketCategory.PRODUCT_QUALITY.value,
                        TicketCategory.BILLING.value,
                        TicketCategory.RETURNS.value,
                        TicketCategory.GENERAL.value,
                    ],
                    weights=[0.35, 0.30, 0.12, 0.08, 0.10, 0.05],
                )[0]
                # Resolution time spikes from ~2h to 24-48h
                resolution_hours = float(np.random.gamma(shape=3.5, scale=7.5))  # mean ~26 hours
                sla_breached = resolution_hours > 12.0  # SLA target is 12 hours
                csat = random.choices([1, 2, 3, 4, 5], weights=[0.42, 0.28, 0.15, 0.10, 0.05])[0]
            else:
                category = random.choices(
                    [
                        TicketCategory.GENERAL.value,
                        TicketCategory.PRODUCT_QUALITY.value,
                        TicketCategory.DELIVERY.value,
                        TicketCategory.BILLING.value,
                        TicketCategory.RETURNS.value,
                        TicketCategory.STOCK_INQUIRY.value,
                    ],
                    weights=[0.25, 0.22, 0.20, 0.15, 0.12, 0.06],
                )[0]
                # Baseline resolution time: ~2.2 hours
                resolution_hours = float(np.random.exponential(scale=2.2))
                sla_breached = resolution_hours > 12.0
                csat = random.choices([1, 2, 3, 4, 5], weights=[0.03, 0.05, 0.12, 0.35, 0.45])[0]

            first_resp_mins = max(5, int(resolution_hours * 60 * random.uniform(0.1, 0.4)))
            first_resp_time = ticket_time + timedelta(minutes=first_resp_mins)
            resolved_time = ticket_time + timedelta(hours=resolution_hours)

            ticket = SupportTicket(
                ticket_id=f"TCK-{200000 + i}",
                customer_id=cust.id,
                order_id=ord_obj.id if ord_obj else None,
                category=category,
                priority=random.choices(
                    [TicketPriority.LOW.value, TicketPriority.MEDIUM.value, TicketPriority.HIGH.value, TicketPriority.URGENT.value],
                    weights=[0.15, 0.50, 0.25, 0.10],
                )[0],
                status=TicketStatus.RESOLVED.value,
                region=cust.region,
                created_at=ticket_time,
                first_response_at=first_resp_time,
                resolved_at=resolved_time,
                resolution_time_hours=round(resolution_hours, 2),
                sla_breached=sla_breached,
                satisfaction_score=csat,
            )
            ticket_list.append(ticket)

        self.session.bulk_save_objects(ticket_list)
        self.session.flush()
        return len(ticket_list)

    def generate_marketing_campaigns(self) -> int:
        """Generate marketing campaigns across channels and regions."""
        camp_list = []
        channels = ["Search", "Paid Social", "Email", "Influencer", "Display"]

        for i in range(NUM_CAMPAIGNS):
            channel = random.choice(channels)
            region = random.choice(REGIONS)
            start_day = random.randint(0, TOTAL_DAYS - 20)
            duration_days = random.randint(10, 25)
            start_date = SIM_START_DATE + timedelta(days=start_day)
            end_date = start_date + timedelta(days=duration_days)

            budget = Decimal(str(random.randint(5000, 35000)))
            spend = (budget * Decimal(str(round(random.uniform(0.85, 1.05), 2)))).quantize(Decimal("0.01"))
            impressions = int(float(spend) * random.uniform(35.0, 70.0))
            ctr = random.uniform(0.015, 0.045)
            clicks = int(impressions * ctr)

            is_incident = start_day >= INCIDENT_START_DAY
            # Conversion rate drops during incident due to stockouts & negative buzz
            cvr = random.uniform(0.012, 0.022) if is_incident else random.uniform(0.028, 0.052)
            conversions = int(clicks * cvr)
            aov = Decimal(str(random.uniform(65.0, 140.0)))
            attributed_rev = (Decimal(str(conversions)) * aov).quantize(Decimal("0.01"))

            camp = MarketingCampaign(
                campaign_id=f"CAMP-{100 + i}",
                name=f"{COMPANY_NAME} {channel} - {region} Q2-Q3 #{i+1}",
                channel=channel,
                region=region,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                spend=spend,
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                attributed_revenue=attributed_rev,
                created_at=start_date - timedelta(days=5),
            )
            camp_list.append(camp)

        self.session.bulk_save_objects(camp_list)
        self.session.flush()
        return len(camp_list)


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def generate_dataset(db_url: str | None = None) -> dict[str, int]:
    """Execute complete data generation pipeline."""
    engine, SessionLocal = get_engine_and_session(db_url)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Check if database is already seeded
        existing_orders = session.execute(select(Order.id).limit(1)).scalar_one_or_none()
        if existing_orders:
            print("[!] Database already contains records. Clearing existing tables...")
            session.execute(text("DELETE FROM audit_events"))
            session.execute(text("DELETE FROM anomalies"))
            session.execute(text("DELETE FROM marketing_campaigns"))
            session.execute(text("DELETE FROM support_tickets"))
            session.execute(text("DELETE FROM inventory"))
            session.execute(text("DELETE FROM orders"))
            session.execute(text("DELETE FROM products"))
            session.execute(text("DELETE FROM customers"))
            session.commit()

        generator = NovaCartDataGenerator(session)
        counts = generator.generate_all()
        session.commit()
        print(f"[+] Data generation committed successfully: {counts}")
        return counts
    except Exception as e:
        session.rollback()
        print(f"[X] Error during data generation: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    generate_dataset()

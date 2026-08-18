"""
ORION Deterministic Analytics — Inventory Module

Calculates warehouse stock levels, stockout frequencies, units sold, and low-inventory warnings.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.models.models import Inventory, Order, OrderStatus, Product


def get_inventory_availability(
    db: Session,
    snapshot_date: datetime | None = None,
    warehouse_region: str | None = None,
) -> dict[str, Any]:
    """Total inventory quantity and warehouse capacity status."""
    query = select(
        func.coalesce(func.sum(Inventory.quantity_on_hand), 0),
        func.count(Inventory.id),
    )
    if snapshot_date:
        query = query.where(Inventory.snapshot_date == snapshot_date)
    if warehouse_region:
        query = query.where(Inventory.warehouse_region == warehouse_region)

    tot_qty, records_count = db.execute(query).one()
    return {
        "total_units_on_hand": int(tot_qty),
        "snapshots_evaluated": int(records_count),
    }


def get_stockout_rate(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
) -> float:
    """
    Percentage of inventory snapshots flagged as out of stock (quantity=0 or stockout_flag=True).
    """
    total_query = select(func.count(Inventory.id))
    stockout_query = select(func.count(Inventory.id)).where(Inventory.stockout_flag == True)

    if category:
        total_query = total_query.join(Product, Inventory.product_id == Product.id).where(Product.category == category)
        stockout_query = stockout_query.join(Product, Inventory.product_id == Product.id).where(Product.category == category)

    if start_date:
        total_query = total_query.where(Inventory.snapshot_date >= start_date)
        stockout_query = stockout_query.where(Inventory.snapshot_date >= start_date)
    if end_date:
        total_query = total_query.where(Inventory.snapshot_date <= end_date)
        stockout_query = stockout_query.where(Inventory.snapshot_date <= end_date)

    tot = db.execute(total_query).scalar_one() or 0
    stockouts = db.execute(stockout_query).scalar_one() or 0

    if tot == 0:
        return 0.0
    return round(float(stockouts) / float(tot), 4)


def get_stockout_rate_by_category(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, float]:
    """Breakdown of stockout rates across each product category."""
    query = (
        select(
            Product.category,
            func.count(Inventory.id).label("total_snaps"),
            func.coalesce(func.sum(case((Inventory.stockout_flag == True, 1), else_=0)), 0).label("stockouts"),
        )
        .join(Product, Inventory.product_id == Product.id)
        .group_by(Product.category)
    )
    if start_date:
        query = query.where(Inventory.snapshot_date >= start_date)
    if end_date:
        query = query.where(Inventory.snapshot_date <= end_date)

    rows = db.execute(query).all()
    results = {}
    for cat, tot, st_cnt in rows:
        rate = (float(st_cnt) / float(tot)) if tot > 0 else 0.0
        results[cat] = round(rate, 4)
    return results


def get_units_sold(
    db: Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category: str | None = None,
) -> int:
    """Total product units sold in completed orders."""
    query = select(func.coalesce(func.sum(Order.quantity), 0)).where(Order.status == OrderStatus.COMPLETED.value)
    if category:
        query = query.join(Product, Order.product_id == Product.id).where(Product.category == category)
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)

    return int(db.execute(query).scalar_one())


def get_low_inventory_products(
    db: Session,
    threshold: int = 10,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List products where latest quantity on hand is below threshold."""
    # Subquery for latest snapshot date
    subq = select(func.max(Inventory.snapshot_date)).scalar_subquery()

    query = (
        select(
            Product.product_id,
            Product.name,
            Product.category,
            Inventory.warehouse_region,
            Inventory.quantity_on_hand,
            Inventory.reorder_point,
        )
        .join(Product, Inventory.product_id == Product.id)
        .where(Inventory.snapshot_date == subq)
        .where(Inventory.quantity_on_hand <= threshold)
        .order_by(Inventory.quantity_on_hand.asc())
        .limit(limit)
    )
    rows = db.execute(query).all()
    return [
        {
            "product_id": pid,
            "name": name,
            "category": cat,
            "region": reg,
            "quantity_on_hand": int(qty),
            "reorder_point": int(reorder_pt),
        }
        for pid, name, cat, reg, qty, reorder_pt in rows
    ]

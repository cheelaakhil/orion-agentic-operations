"""Initial database schema for NovaCart business data and ORION operational tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. customers
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('segment', sa.String(length=32), nullable=False),
        sa.Column('region', sa.String(length=64), nullable=False),
        sa.Column('first_order_date', sa.DateTime(), nullable=True),
        sa.Column('lifetime_value', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_customers_customer_id', 'customers', ['customer_id'], unique=True)
    op.create_index('ix_customers_email', 'customers', ['email'], unique=False)
    op.create_index('ix_customers_segment', 'customers', ['segment'], unique=False)
    op.create_index('ix_customers_region', 'customers', ['region'], unique=False)
    op.create_index('ix_customers_created_at', 'customers', ['created_at'], unique=False)

    # 2. products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('list_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_product_id', 'products', ['product_id'], unique=True)
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    op.create_index('ix_products_category', 'products', ['category'], unique=False)

    # 3. orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.String(length=64), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('region', sa.String(length=64), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('order_date', sa.DateTime(), nullable=False),
        sa.Column('fulfilled_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_order_id', 'orders', ['order_id'], unique=True)
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'], unique=False)
    op.create_index('ix_orders_product_id', 'orders', ['product_id'], unique=False)
    op.create_index('ix_orders_region', 'orders', ['region'], unique=False)
    op.create_index('ix_orders_status', 'orders', ['status'], unique=False)
    op.create_index('ix_orders_order_date', 'orders', ['order_date'], unique=False)
    op.create_index('ix_orders_date_region', 'orders', ['order_date', 'region'], unique=False)
    op.create_index('ix_orders_customer_date', 'orders', ['customer_id', 'order_date'], unique=False)

    # 4. inventory
    op.create_table(
        'inventory',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_region', sa.String(length=64), nullable=False),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False),
        sa.Column('reorder_point', sa.Integer(), nullable=False),
        sa.Column('stockout_flag', sa.Boolean(), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(), nullable=False),
        sa.Column('last_restock_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_inventory_product_id', 'inventory', ['product_id'], unique=False)
    op.create_index('ix_inventory_warehouse_region', 'inventory', ['warehouse_region'], unique=False)
    op.create_index('ix_inventory_stockout_flag', 'inventory', ['stockout_flag'], unique=False)
    op.create_index('ix_inventory_snapshot_date', 'inventory', ['snapshot_date'], unique=False)
    op.create_index('ix_inventory_product_snapshot', 'inventory', ['product_id', 'snapshot_date'], unique=False)
    op.create_index('ix_inventory_region_snapshot', 'inventory', ['warehouse_region', 'snapshot_date'], unique=False)

    # 5. support_tickets
    op.create_table(
        'support_tickets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', sa.String(length=64), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('priority', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('region', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('first_response_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_time_hours', sa.Float(), nullable=True),
        sa.Column('sla_breached', sa.Boolean(), nullable=False),
        sa.Column('satisfaction_score', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_support_tickets_ticket_id', 'support_tickets', ['ticket_id'], unique=True)
    op.create_index('ix_support_tickets_customer_id', 'support_tickets', ['customer_id'], unique=False)
    op.create_index('ix_support_tickets_order_id', 'support_tickets', ['order_id'], unique=False)
    op.create_index('ix_support_tickets_category', 'support_tickets', ['category'], unique=False)
    op.create_index('ix_support_tickets_status', 'support_tickets', ['status'], unique=False)
    op.create_index('ix_support_tickets_region', 'support_tickets', ['region'], unique=False)
    op.create_index('ix_support_tickets_created_at', 'support_tickets', ['created_at'], unique=False)
    op.create_index('ix_support_tickets_sla_breached', 'support_tickets', ['sla_breached'], unique=False)
    op.create_index('ix_tickets_created_sla', 'support_tickets', ['created_at', 'sla_breached'], unique=False)
    op.create_index('ix_tickets_region_created', 'support_tickets', ['region', 'created_at'], unique=False)

    # 6. marketing_campaigns
    op.create_table(
        'marketing_campaigns',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('channel', sa.String(length=64), nullable=False),
        sa.Column('region', sa.String(length=64), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('budget', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('spend', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('impressions', sa.Integer(), nullable=False),
        sa.Column('clicks', sa.Integer(), nullable=False),
        sa.Column('conversions', sa.Integer(), nullable=False),
        sa.Column('attributed_revenue', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_marketing_campaigns_campaign_id', 'marketing_campaigns', ['campaign_id'], unique=True)
    op.create_index('ix_marketing_campaigns_channel', 'marketing_campaigns', ['channel'], unique=False)
    op.create_index('ix_marketing_campaigns_region', 'marketing_campaigns', ['region'], unique=False)
    op.create_index('ix_marketing_campaigns_start_date', 'marketing_campaigns', ['start_date'], unique=False)
    op.create_index('ix_marketing_campaigns_end_date', 'marketing_campaigns', ['end_date'], unique=False)

    # 7. audit_events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('actor', sa.String(length=128), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_events_entity_type', 'audit_events', ['entity_type'], unique=False)
    op.create_index('ix_audit_events_entity_id', 'audit_events', ['entity_id'], unique=False)
    op.create_index('ix_audit_events_timestamp', 'audit_events', ['timestamp'], unique=False)

    # 8. anomalies
    op.create_table(
        'anomalies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('anomaly_id', sa.String(length=64), nullable=False),
        sa.Column('metric_name', sa.String(length=128), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('baseline_value', sa.Float(), nullable=False),
        sa.Column('deviation_pct', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('affected_dimension', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('onset_date', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomalies_anomaly_id', 'anomalies', ['anomaly_id'], unique=True)
    op.create_index('ix_anomalies_metric_name', 'anomalies', ['metric_name'], unique=False)
    op.create_index('ix_anomalies_severity', 'anomalies', ['severity'], unique=False)
    op.create_index('ix_anomalies_affected_dimension', 'anomalies', ['affected_dimension'], unique=False)
    op.create_index('ix_anomalies_status', 'anomalies', ['status'], unique=False)
    op.create_index('ix_anomalies_detected_at', 'anomalies', ['detected_at'], unique=False)


def downgrade() -> None:
    op.drop_table('anomalies')
    op.drop_table('audit_events')
    op.drop_table('marketing_campaigns')
    op.drop_table('support_tickets')
    op.drop_table('inventory')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('customers')

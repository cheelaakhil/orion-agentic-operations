# ORION Database

## Structure

```
database/
├── migrations/    # Alembic database migrations
│   └── README.md
├── seeds/         # Synthetic dataset generation
│   └── README.md
└── README.md
```

## Setup

1. Ensure PostgreSQL 15+ is running
2. Create the database: `createdb orion`
3. Run migrations: `cd backend && alembic upgrade head`
4. Seed data: `python -m database.seeds.generate`

## Schema

See [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for full schema definition.

### Business Tables
- `orders` — Customer orders with revenue data
- `products` — Product catalog
- `customers` — Customer profiles and segments
- `inventory` — Inventory snapshots by warehouse
- `support_tickets` — Support ticket lifecycle
- `marketing_campaigns` — Campaign performance data

### System Tables
- `anomalies` — Detected anomalies
- `investigations` — Investigation records
- `investigation_steps` — Per-agent step tracking
- `approval_requests` — Human approval workflow
- `action_executions` — Action execution log
- `audit_logs` — Immutable audit trail

# Alembic Migrations

Database migration files will be generated here using Alembic.

## Commands

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

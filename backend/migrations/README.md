# Database migrations

The application creates the baseline schema automatically for local bootstrap. For a production rollout, use Alembic against PostgreSQL and commit generated revisions here.

Example:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Do not point production at SQLite for multi-instance deployments.

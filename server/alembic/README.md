# Alembic (optional)

This directory enables Python-native migrations for future changes.

- Baseline the current DB by stamping the baseline revision:

```
cd server
alembic stamp base
```

- Create a new revision:

```
alembic revision -m "add something" --autogenerate
alembic upgrade head
```

Note: Current schema was established via /db SQL migrations. Use Alembic for incremental changes going forward if preferred.

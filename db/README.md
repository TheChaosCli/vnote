# Database

PostgreSQL-first schema with SQL migrations and seed data.

- Migrations live in `/db/migrations` and apply in lexicographic order.
- Seeds live in `/db/seed` and are safe to run on an empty DB.
- Requires Postgres extensions: `citext`, `ltree` (optional).

Apply (local):

- psql "$DB_URL" -f db/migrations/0001_init.sql
- psql "$DB_URL" -f db/seed/seed.sql

Rollback: manual for now; see notes at end of each migration.

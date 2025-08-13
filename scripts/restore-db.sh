#!/usr/bin/env bash
set -euo pipefail

# Restore PostgreSQL database from a compressed dump. Destroys current schema.
# Env:
# - DB_URL: postgres connection string
# Arg:
# - path to db-*.sql.gz

if [[ $# -lt 1 ]]; then
  echo "Usage: BACKUP=db-YYYYMMDD-HHMMSS.sql.gz DB_URL=... ./scripts/restore-db.sh <dump.gz>" >&2
  exit 1
fi

DUMP="$1"
if [[ -z "${DB_URL:-}" ]]; then
  echo "ERROR: DB_URL not set" >&2
  exit 1
fi

echo "Restoring DB from $DUMP"
gunzip -c "$DUMP" | psql "$DB_URL"
echo "Restore complete."


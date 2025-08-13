#!/usr/bin/env bash
set -euo pipefail

# Backup PostgreSQL database and optional attachments directory.
# Env:
# - DB_URL: postgres connection string (e.g., postgres://user:pass@localhost:5432/db)
# - BACKUP_DIR: destination directory (default: ./backups)
# - ATTACHMENTS_DIR: path to attachments (optional)

BACKUP_DIR=${BACKUP_DIR:-"./backups"}
STAMP=$(date +"%Y%m%d-%H%M%S")
mkdir -p "$BACKUP_DIR"

if [[ -z "${DB_URL:-}" ]]; then
  echo "ERROR: DB_URL not set" >&2
  exit 1
fi

DB_DUMP="$BACKUP_DIR/db-$STAMP.sql.gz"
echo "Backing up DB to $DB_DUMP"
pg_dump --no-owner --if-exists "$DB_URL" | gzip -9 > "$DB_DUMP"

if [[ -n "${ATTACHMENTS_DIR:-}" && -d "$ATTACHMENTS_DIR" ]]; then
  TAR_PATH="$BACKUP_DIR/attachments-$STAMP.tar.gz"
  echo "Archiving attachments to $TAR_PATH"
  tar -C "$ATTACHMENTS_DIR" -czf "$TAR_PATH" .
fi

echo "Backup complete."


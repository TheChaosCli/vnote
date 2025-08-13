# Security, Backups, and Deployment

## Security

- HTTPS: enforce TLS via reverse proxy; HSTS; secure cookies; strict CORS.
- CSP: default‑src 'self'; explicitly allow assets; no unsafe‑inline.
- Auth: password‑based with Argon2; session cookies or JWT (short‑lived) + refresh.
- Secrets: stored in .env, not in VCS; rotate regularly; least‑privilege DB user.
- Access Control: single‑user scoping initially; later per‑space permissions.
- Input Safety: sanitize uploads; optional antivirus scan for attachments.
- Rate Limiting: auth and sync endpoints; IP and user scoped.
- Logging: avoid PII; structured logs; audit version restores and deletes.

## Backups

- Schedule: daily full DB dump; hourly WAL/incremental (Postgres) optional.
- Scope: database + attachments; include schema and seeds version.
- Destinations: local path, network share, S3/B2 with encryption at rest.
- Verification: restore into ephemeral DB and run integrity checks.
- Scripts: /scripts/backup-* and /scripts/restore-* with env‑configurable targets.

## Deployment

- Docker Compose: db, server, web, websocket (optional), backup sidecar.
- Reverse Proxy: Caddy/Traefik/Nginx for TLS and headers.
- Observability: health checks, metrics endpoint, log shipping.
- Configuration: .env.example maintained; secrets injected at runtime.


# Architecture Overview

Local‑first, self‑hosted architecture with a modular monorepo:

- frontend: React + Vite web app (editor, graph, views, settings).
- server: Node/Express or Python/FastAPI API with auth, REST, optional WebSockets for collaboration; background jobs.
- packages/editor: Tiptap‑based block/Markdown components and extensions.
- packages/importers: Evernote/Joplin/Obsidian/Standard Notes/Markdown adapters.
- packages/sync: Client/server sync logic and conflict resolution primitives.
- db: Migrations and seeds for PostgreSQL/MariaDB; attachments config.
- assets: Static icons, themes, images; CSP‑safe delivery.
- scripts: Backup/restore and maintenance.
- tests: Integration/e2e fixtures; importer test data.

## Data Flow

1) Frontend renders from local cache (Dexie) for instant interactions.
2) Writes apply to local cache and enqueue for sync.
3) Sync module batches mutations to server via REST; attachments stream separately.
4) Server writes to DB, issues version numbers, and broadcasts updates via WebSockets (if enabled).
5) Clients reconcile via CRDT (for blocks) or field‑wise merge (metadata).

## Components

- Editor: Tiptap nodes for paragraph, heading, lists, table, codeBlock, math, image, attachment embeds, callouts, and custom blocks.
- Graph: Client‑side computed graph from links; server provides link index for large sets.
- Search: Server‑side full‑text (Postgres tsvector) with client highlights.
- Attachments: Stored on disk or object storage (S3/B2); signed URLs; virus scan hook (optional).
- Backups: Scheduled DB dumps + attachments archive; restore verification script.

## Technology Choices

- Frontend: React 18, TypeScript, Vite, React Router, TanStack Query, Zustand, Tailwind + Radix UI.
- Collaboration: Yjs, y‑websocket (optional), IndexedDB via Dexie.
- Backend: Node/Express or FastAPI; choose per team expertise. JWT or session cookies; Argon2 password hashing.
- Database: PostgreSQL preferred; MariaDB compatible. Migrations via Prisma/Knex (Node) or Alembic (Python).
- Observability: pino/loguru logs, health endpoints, basic metrics.

## Sequence: Edit → Sync → Merge (Happy Path)

1) User edits a paragraph block; Tiptap updates Yjs doc.
2) Local store updates block state and note’s updatedAt; enqueue mutation.
3) Sync sends delta or CRDT update; server validates and persists block snapshot.
4) Server responds with versionId and state vector; client marks confirmed.
5) Other clients receive broadcast and apply via Yjs awareness.

## Deployment

- Docker Compose stack: DB, server, web, optional websocket, and backup sidecar.
- Single‑binary server (future): embedded job runner and websocket.
- HTTPS termination at reverse proxy (Caddy/Traefik/Nginx) with CSP and HSTS.


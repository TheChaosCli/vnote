# Roadmap

## Phase 0 — Foundations

- Repo scaffolding and CI; lint/format; basic health checks.
- DB migrations: users, folders, notes, blocks, tags, links, attachments.
- Minimal server with auth and CRUD for notes/blocks/tags.

## Phase 1 — MVP

- Editor: Markdown + WYSIWYG parity for core nodes/marks.
- Backlinks + basic graph view; search index.
- Attachments upload + preview; version history (note‑level).
- Offline cache (Dexie) and background sync; conflict policy.
- Import: Markdown folder + Obsidian vault; baseline Evernote/Standard Notes.
- Backups: scheduled DB + attachments; restore script with verification.

## Phase 2 — Power User

- Properties and database‑like views (table/board/calendar/gallery).
- Templates and slash‑menu customization.
- Advanced graph filters and clustering.
- Improved importer coverage and link rewriting.

## Phase 3 — Collaboration (Optional/Advanced)

- Yjs live collaboration via websocket; presence and cursors.
- Shared spaces and per‑space permissions.
- Mobile apps with offline sync.

## Phase 4 — Hardening

- Performance tuning (large vaults), backup restore drills, e2e tests.
- Security review; rate limits, CSP tightening, attachment scanning.


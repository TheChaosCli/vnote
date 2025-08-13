# Repository Guidelines

## Project Structure & Module Organization
- `/frontend`: Web app (React + Vite). Block editor, graph, tagging.
- `/server`: API (Node/Express or Python/FastAPI), auth, WebSockets, jobs.
- `/packages/editor`: Block + Markdown/WYSIWYG components and extensions.
- `/packages/importers`: Evernote (.enex), Joplin (.jex), Obsidian vault, Standard Notes JSON.
- `/packages/sync`: Client/server sync logic and conflict resolution.
- `/db`: Migrations and seed data (PostgreSQL/MariaDB). Attachments storage config.
- `/assets`: Static files (icons, themes, images).
- `/docs`: Design notes, ADRs, architecture diagrams.
- `/scripts`: Backup/restore, local dev, maintenance.
- `/tests`: Integration/e2e and cross-package fixtures.

## Build, Test, and Development Commands
- Frontend: `cd frontend && npm run dev` (Vite dev server), `npm run build` (prod), `npm test`.
- Server (Node): `cd server && npm run dev`, `npm test`. Server (Python): `uvicorn app.main:app --reload`, `pytest -q`.
- Importers: `cd packages/importers && npm test` or `pytest -q` (depending on language).
- Lint/format: `npm run lint && npm run format` or `ruff check && black .`.

## Coding Style & Naming Conventions
- Indentation: 2 spaces (JS/TS), 4 spaces (Python).
- JS/TS: ESLint + Prettier. Names: `kebab-case` files, `PascalCase` components, `camelCase` vars.
- Python: Ruff/Flake8 + Black + isort. Names: `snake_case` modules/functions, `CamelCase` classes.
- Commits: Conventional Commits (e.g., `feat: backlinks graph`, `fix(sync): resolve tombstone merge`).

## Frontend Stack Defaults
- Framework: React 18+ with TypeScript, Vite, React Router.
- Editor: Tiptap (ProseMirror) with Markdown + rich text; code/Math extensions.
- Collaboration: Yjs (CRDT) + y-websocket for real-time; Dexie/IndexedDB for offline cache.
- Data: TanStack Query for server state; Zustand for UI state.
- UI: Tailwind CSS + Radix UI primitives (optionally shadcn/ui).
- Tests: Vitest + React Testing Library; Playwright for e2e.

## Testing Guidelines
- Frontend: Vitest/Jest + Testing Library (`*.test.ts[x]` near sources).
- Backend: Pytest or Jest (mirror module path under `tests/` or co-located).
- Importers: use fixtures for `.enex`, `.jex`, Markdown; verify tags, timestamps, links.
- Sync: simulate offline/merge conflicts; verify deterministic resolution.
- Coverage: 80%+ on changed code. `npm test -- --coverage` or `pytest --cov`.

## Commit & Pull Request Guidelines
- PRs: summary, scope, linked issue, migrations/rollback notes, and screenshots/GIFs for UI (editor/graph/import flows).
- Keep diffs focused; update `/docs` on behavior or schema changes.
- CI green; include/adjust tests for new behavior.

## Architecture Overview
- Local-first, self-hosted DB (PostgreSQL/MariaDB) with attachments; API exposes REST + optional WebSockets for collaboration.
- Block-based editor supports Markdown and rich text with versioning; files stored as notes + metadata.
- Sync service propagates changes across clients with conflict handling and offline caches.
- Backups via `/scripts/backup-*` to local path, network share, or S3/B2; include restore verification.
- Import pipeline preserves structure, tags, dates, and links where supported.

## Security & Configuration
- Secrets in `.env` files; commit `.env.example` only. Enforce HTTPS and set CSP headers.
- Least-privilege DB users; rotate keys; encrypt backups at rest. Avoid PII in logs.

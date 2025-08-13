# VNote — Self‑Hosted, Local‑First Notes (Concept Scaffold)

This repo contains design docs and a minimal Dockerized FastAPI + Postgres backend to bootstrap development.

- Docs: see `/docs` for concept, architecture, data model, sync, imports, API, security, and roadmap.
- Backend: `/server` FastAPI app with DB‑backed auth and basic notes endpoints.
- Database: `/db` SQL migrations and seed.
- Scripts: `/scripts` backup/restore helpers.

## Run with Docker

- docker compose up --build
- API: http://localhost:8000

Apply migrations and seed run automatically at startup.

## Auth

- Register: POST /auth/register { email, password } → returns `{ accessToken }`
- Login: POST /auth/login { email, password } → `{ accessToken }`
- Send `Authorization: Bearer <accessToken>` to access notes endpoints.

Example:

- curl -sX POST http://localhost:8000/auth/register -H 'Content-Type: application/json' -d '{"email":"you@example.com","password":"pass"}'
- curl -s http://localhost:8000/notes -H 'Authorization: Bearer <token>'

## Data Endpoints

- Tags: GET/POST/PATCH/DELETE `/tags`
- Folders: GET `/folders/tree`, POST/PATCH/DELETE `/folders`
- Attachments: POST `/attachments`, GET `/attachments/:id`, GET `/attachments/:id/download`
- Search: GET `/search?q=term` (title/excerpt)
- Backlinks: GET `/notes/:id/backlinks`
- Graph: GET `/graph` (limited edges)

## Code Repositories (MVP)

- Create/list repos: POST/GET `/repos`
- Files: GET `/repos/:id/files`, GET `/repos/:id/files/{path}`
- Upsert file + commit: POST `/repos/:id/files?path=...&message=...` with `content` or `attachmentId`
- Multi-file commit: POST `/repos/:id/commit` with `{ message, branch?, files: [{ path, content?, attachmentId? }] }`
- Commits: GET `/repos/:id/commits`
- Diff: GET `/repos/:id/diff?commitA=...&commitB=...&path=...`
- Repo search: GET `/repos/:id/search?q=term` (latest file contents)

## Blocks (CRDT)

- Create block: POST `/notes/:id/blocks` with `{ type, attrs?, after? }`
- Update block: PATCH `/blocks/:id` with `{ attrs?, order? }`
- Push CRDT update: POST `/blocks/:id/crdt` with binary body; server stores versioned payloads
  - Server uses y-py to decode prosemirror snapshots when possible and updates the note’s plain text + search index.

## Frontend (minimal)

- cd frontend && npm install && npm run dev
- Proxies `/auth`, `/notes`, `/tags`, `/folders`, `/attachments`, `/search`, `/repos` to the API at 8000.
- UI covers register/login, list/create notes, tag create/list, folder tree create/list, attachments upload, and basic search.

## Testing (API)

- cd server && pip install -r requirements.txt
- Ensure a Postgres DB is reachable at `DB_URL` and migrations are applied (use docker compose)
- Run tests: `pytest -q`

## Migrations

- SQL migrations live in `/db` and run via docker-compose `migrate` service.
- Optional Alembic exists under `/server/alembic` for Python-native migrations going forward.

Notes
- This is a simple, DB-backed versioning model to manage code and text files inside the notes system. Future upgrades can integrate Git or external VCS.

## Docker Notes

- Healthchecks ensure DB is ready before running migrations and API.
- Attachments persist in the `attachments` volume (mapped at `/data/attachments`).

## Next

- Wire remaining endpoints (tags, folders, attachments) to DB
- Add Alembic migrations or keep raw SQL
- Add CORS, rate limits, and production Docker hardening per `/docs/security-backup-deploy.md`

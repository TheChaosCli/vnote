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

## Next

- Wire remaining endpoints (tags, folders, attachments) to DB
- Add Alembic migrations or keep raw SQL
- Add CORS, rate limits, and production Docker hardening per `/docs/security-backup-deploy.md`

# Server (FastAPI)

FastAPI server matching the API outline. Auth uses DB-backed bearer sessions with Argon2; notes are scoped to the authenticated user.

Run (dev):

- cd server
- pip install -r requirements.txt
- export DB_URL=postgres://vnote:vnote@localhost:5432/vnote
- uvicorn app.main:app --reload

Environment variables (see .env.example at repo root):

- DB_URL: PostgreSQL connection string
- SECRET_KEY: for token signing (placeholder)

Docker Compose (dev):

- docker compose up --build
- API base: http://localhost:8000

Quick start (auth):

- Register: curl -sX POST http://localhost:8000/auth/register -H 'Content-Type: application/json' -d '{"email":"you@example.com","password":"pass"}'
- Get token from response and use: `-H "Authorization: Bearer <token>"`
- Create note: curl -sX POST http://localhost:8000/notes -H 'Authorization: Bearer <token>' -H 'Content-Type: application/json' -d '{"title":"Hello"}'

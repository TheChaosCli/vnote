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

Tags

- List: GET /tags
- Create: POST /tags { name, color? }
- Update: PATCH /tags/:id { name?, color? }
- Delete: DELETE /tags/:id

Folders

- Tree: GET /folders/tree → { roots: [{ id, name, parentId, children: [] }] }
- Create: POST /folders { name, parentId? }
- Update: PATCH /folders/:id { name?, parentId? }
- Delete: DELETE /folders/:id (requires empty)

Attachments

- Upload: POST /attachments (multipart form-data with file)
- Meta: GET /attachments/:id → { id, name, mime, url }
- Download: GET /attachments/:id/download

CORS

- Configure allowed origins with `CORS_ALLOW_ORIGINS` (comma-separated). Compose defaults to localhost dev ports.

Search & Links

- Search: GET /search?q=term → ranked results with snippets
- Backlinks: GET /notes/:id/backlinks → referring notes + counts
- Graph: GET /graph → nodes/edges from links table (limited)
- Reindex: POST /admin/reindex-search — rebuilds search index from title/excerpt/plain_text

Code Repositories

- Create/list: POST/GET /repos
- Files: GET /repos/:id/files, GET /repos/:id/files/{path}
- Upsert + commit single file: POST /repos/:id/files?path=...&message=... with `content` or `attachmentId`
- Multi-file commit: POST /repos/:id/commit with JSON { message, branch?: "main", files: [{ path, content? , attachmentId? }] }
- Commits: GET /repos/:id/commits
- Diff: GET /repos/:id/diff?commitA=...&commitB=...&path=...
- Search: GET /repos/:id/search?q=... → simple content match and language hint

Limits & Compression

- RATE_LIMIT_PER_MIN: default 120 requests/min (per IP)
- MAX_BODY_BYTES: default 10MB
- GZipMiddleware enabled (responses > 500 bytes)

Testing

- cd server && pip install -r requirements.txt
- Ensure DB_URL points to a PostgreSQL instance with migrations applied (docker compose up will do this)
- pytest -q
Blocks (CRDT payloads)

- Create: POST /notes/:id/blocks { type, attrs?, after? }
- Update: PATCH /blocks/:id { attrs?, order? }
- Push CRDT: POST /blocks/:id/crdt (octet-stream payload saved as a new version)
  - Server attempts to decode Yjs prosemirror fragment via y-py and rebuilds note plaintext from latest block snapshots to keep search index updated.

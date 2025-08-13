# API Outline (Draft)

REST‑first with optional WebSockets for collaboration. All routes scoped by authenticated user.

## Auth

- POST /auth/register — email, password
- POST /auth/login — email, password
- POST /auth/logout
- POST /auth/refresh

## Notes & Blocks

- GET /notes?folder=…&q=…&tag=…&page=…
- POST /notes — { title, folderId, tags, properties }
- GET /notes/:id — includes blocks and basic backlinks
- PATCH /notes/:id — metadata only
- DELETE /notes/:id — soft delete; tombstone

- POST /notes/:id/blocks — create block
- PATCH /blocks/:id — update attrs/order
- DELETE /blocks/:id
- POST /blocks/:id/crdt — Yjs update payload

## Tags

- GET /tags — list with usage counts
- POST /tags — create
- PATCH /tags/:id — rename/color/alias
- DELETE /tags/:id — reassign/remove

## Folders

- GET /folders/tree
- POST /folders — { name, parentId }
- PATCH /folders/:id
- DELETE /folders/:id

## Links & Graph

- GET /notes/:id/backlinks
- GET /graph?scope=folder|tag&limit=…

## Attachments

- POST /attachments — multipart upload, checksum
- GET /attachments/:id — signed URL or streamed content
- DELETE /attachments/:id

## Search

- GET /search?q=…&page=… — full‑text with snippets

## Sync

- GET /sync — delta pull
- POST /sync — batch push

## Admin

- GET /health — liveness/readiness
- POST /backup/run — trigger backup (if enabled)


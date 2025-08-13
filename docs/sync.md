# Sync & Conflict Resolution

Local‑first sync that prioritizes correctness and determinism while remaining simple for single‑user setups and scalable to optional multi‑user collaboration.

## Overview

- Blocks use CRDT (Yjs) for concurrent text edits.
- Metadata (title, tags, folder, properties) uses field‑wise last‑write‑wins with vector clocks.
- Attachments upload via separate channel with checksums and resumable support.

## Client State

- client_id: stable UUID per device.
- clock: per‑entity logical version; vector or lamport per record.
- state_vector: Yjs state for block content.

## Protocol (Baseline)

- Pull: GET /sync?since=ts&clock=… → returns changed notes/blocks/tags/links + tombstones.
- Push: POST /sync with batches: { entity, op, data, clock, deps }.
- CRDT: POST /blocks/:id/crdt with Yjs update; server merges into latest snapshot.
- Attachments: POST /attachments (multipart) with checksum; server dedupes.

## Conflict Policy

- Blocks: CRDT merge via Yjs; always converges.
- Metadata: compare per‑field clock; higher timestamp/clock wins; for ties, merge sets (e.g., tags) and prefer deterministic key order.
- Deletions: tombstones trump updates if newer; edits after delete resurrect only if user explicit restore.

## Integrity & Idempotency

- All mutations carry client_id and clock; server deduplicates.
- Attachments verified via sha256 checksum; server returns canonical storage_key.

## Security

- Authenticated requests with short‑lived tokens; refresh via session.
- Rate‑limit sync endpoints; per‑user quotas on batch size and frequency.

## Rebuild & Repair

- Rebuild search index from notes/blocks snapshots.
- Recompute backlinks and graph from links table.
- Validate attachments store against DB and report orphans.

## WebSockets (Optional)

- Channel: note/:id for live block updates and awareness.
- Events: block_update, note_meta_update, link_update.


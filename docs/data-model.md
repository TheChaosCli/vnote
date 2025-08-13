# Data Model (Draft)

PostgreSQL‑first schema; MariaDB compatible. Names are indicative; finalize via migrations.

## Core Entities

- users
  - id (uuid), email (citext, unique), password_hash, created_at, updated_at
  - profile: display_name, avatar_url (nullable)

- sessions/tokens
  - id, user_id → users.id, created_at, expires_at, last_seen_at, user_agent, ip

- folders
  - id, user_id, name, parent_id (nullable), path_ltree (Postgres ltree), created_at, updated_at

- notes
  - id, user_id, title, slug, folder_id (nullable), excerpt, created_at, updated_at, deleted_at (nullable)
  - status: archived (bool), pinned (bool)

- blocks
  - id, note_id → notes.id, type (enum), attrs (jsonb), order_idx (numeric), created_at, updated_at
  - content model held by CRDT snapshots; attrs include language, level, etc.

- block_versions
  - id, block_id → blocks.id, version, ydoc_snapshot (bytea/jsonb), created_at

- note_versions
  - id, note_id, version, snapshot (jsonb), created_at, created_by

- tags
  - id, user_id, name (unique per user), color (nullable), alias_of (nullable)

- note_tags
  - note_id → notes.id, tag_id → tags.id (composite pk)

- links
  - id, src_note_id, dst_note_id, src_block_id (nullable), label (nullable), created_at

- attachments
  - id, user_id, note_id (nullable), name, mime, bytes, checksum (sha256), storage_key, created_at, created_by

- properties_definitions
  - id, user_id, name, type (text/number/date/select/multi), options (jsonb), created_at

- note_properties
  - note_id, property_id → properties_definitions.id, value (jsonb)

- sync_state
  - id, user_id, client_id, last_pulled_at, last_pushed_at, clock (jsonb), state_vector (bytea)

- tombstones
  - id, entity (enum), entity_id (uuid), deleted_at, cause (text)

## Indexing & Constraints

- notes (user_id, updated_at desc), (folder_id), slug unique per user
- blocks (note_id, order_idx), (updated_at), partial index for type filters
- tags (user_id, lower(name) unique)
- links (src_note_id), (dst_note_id)
- attachments (user_id, checksum), storage_key unique
- Full‑text: generated tsvector for notes(title + plain_text_content)

## Full‑Text Strategy

- Store block plain text in a materialized “note_search” view or trigger‑maintained denormalized table for fast search without querying CRDT payloads.

## Permissions (Initial)

- Single‑user instance: enforce user_id scoping; later extend to shared spaces.

## Migrations

- Prefer incremental migrations with rollback notes in /db. Include seed fixtures for tests and importer validation.


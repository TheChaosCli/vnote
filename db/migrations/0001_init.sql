-- 0001_init.sql — Core schema (PostgreSQL)
-- Extensions
CREATE EXTENSION IF NOT EXISTS citext;
DO $$ BEGIN
  CREATE EXTENSION IF NOT EXISTS ltree;
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'ltree not available; path_ltree columns will be text';
END $$;

-- Users and sessions
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email CITEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  last_seen_at TIMESTAMPTZ,
  user_agent TEXT,
  ip INET
);

-- Folders
CREATE TABLE IF NOT EXISTS folders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  parent_id UUID REFERENCES folders(id) ON DELETE SET NULL,
  path_ltree LTREE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_folders_user ON folders(user_id);

-- Notes
CREATE TABLE IF NOT EXISTS notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT,
  folder_id UUID REFERENCES folders(id) ON DELETE SET NULL,
  excerpt TEXT,
  archived BOOLEAN NOT NULL DEFAULT false,
  pinned BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_notes_user_slug ON notes(user_id, slug) WHERE slug IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notes_folder ON notes(folder_id);
CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(user_id, updated_at DESC);

-- Blocks
CREATE TYPE block_type AS ENUM (
  'paragraph','heading','blockquote','bulleted_list','ordered_list','list_item','code','table','image','attachment','callout','math','divider','todo'
);
CREATE TABLE IF NOT EXISTS blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  type block_type NOT NULL,
  attrs JSONB NOT NULL DEFAULT '{}',
  order_idx NUMERIC NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_blocks_note_order ON blocks(note_id, order_idx);
CREATE INDEX IF NOT EXISTS idx_blocks_updated ON blocks(updated_at);

-- Versions
CREATE TABLE IF NOT EXISTS block_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  block_id UUID NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
  version BIGINT NOT NULL,
  ydoc_snapshot BYTEA NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_block_versions ON block_versions(block_id, version);

CREATE TABLE IF NOT EXISTS note_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  version BIGINT NOT NULL,
  snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES users(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_note_versions ON note_versions(note_id, version);

-- Tags
CREATE TABLE IF NOT EXISTS tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  color TEXT,
  alias_of UUID REFERENCES tags(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_tags_user_name ON tags(user_id, lower(name));

CREATE TABLE IF NOT EXISTS note_tags (
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

-- Links
CREATE TABLE IF NOT EXISTS links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  src_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  dst_note_id UUID REFERENCES notes(id) ON DELETE SET NULL,
  src_block_id UUID REFERENCES blocks(id) ON DELETE SET NULL,
  label TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_links_src ON links(src_note_id);
CREATE INDEX IF NOT EXISTS idx_links_dst ON links(dst_note_id);

-- Attachments
CREATE TABLE IF NOT EXISTS attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  note_id UUID REFERENCES notes(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  mime TEXT,
  bytes BIGINT,
  checksum TEXT NOT NULL,
  storage_key TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_attachments_user_checksum ON attachments(user_id, checksum);

-- Properties
CREATE TYPE property_type AS ENUM ('text','number','date','select','multi');
CREATE TABLE IF NOT EXISTS properties_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type property_type NOT NULL,
  options JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_propdef_user_name ON properties_definitions(user_id, name);

CREATE TABLE IF NOT EXISTS note_properties (
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  property_id UUID NOT NULL REFERENCES properties_definitions(id) ON DELETE CASCADE,
  value JSONB,
  PRIMARY KEY (note_id, property_id)
);

-- Sync state and tombstones
CREATE TABLE IF NOT EXISTS sync_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id UUID NOT NULL,
  last_pulled_at TIMESTAMPTZ,
  last_pushed_at TIMESTAMPTZ,
  clock JSONB,
  state_vector BYTEA
);
CREATE INDEX IF NOT EXISTS idx_sync_state_user_client ON sync_state(user_id, client_id);

CREATE TYPE entity_type AS ENUM ('note','block','tag','folder','attachment','link','property');
CREATE TABLE IF NOT EXISTS tombstones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity entity_type NOT NULL,
  entity_id UUID NOT NULL,
  deleted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  cause TEXT
);

-- Full-text search (materialized strategy placeholder)
CREATE TABLE IF NOT EXISTS note_search (
  note_id UUID PRIMARY KEY REFERENCES notes(id) ON DELETE CASCADE,
  content_tsv tsvector
);
CREATE INDEX IF NOT EXISTS idx_note_search_gin ON note_search USING GIN(content_tsv);

-- Triggers placeholders (implement via functions in later migration)

-- Rollback notes: drop tables in reverse dependency order; drop types; drop extensions if desired.


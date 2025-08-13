-- 0004_notes_plain_text.sql — Add plain_text to notes for indexing
ALTER TABLE notes ADD COLUMN IF NOT EXISTS plain_text TEXT;


-- 0002_search_index.sql — GIN index for title/excerpt search
CREATE INDEX IF NOT EXISTS idx_notes_search ON notes USING GIN (
  to_tsvector('english', coalesce(title,'') || ' ' || coalesce(excerpt,''))
);


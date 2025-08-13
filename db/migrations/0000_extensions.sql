-- 0000_extensions.sql — Required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;
DO $$ BEGIN
  CREATE EXTENSION IF NOT EXISTS ltree;
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'ltree not available';
END $$;


-- Seed minimal data for development
INSERT INTO users (id, email, password_hash, display_name)
VALUES (
  gen_random_uuid(),
  'demo@example.com',
  '$argon2id$v=19$m=65536,t=3,p=2$DEMO$HASH',
  'Demo User'
)
ON CONFLICT (email) DO NOTHING;

-- Optional: a root folder
INSERT INTO folders (id, user_id, name, parent_id)
SELECT gen_random_uuid(), u.id, 'Root', NULL FROM users u WHERE u.email='demo@example.com'
ON CONFLICT DO NOTHING;


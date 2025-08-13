-- 0005_repos_branches_multifile.sql — Branches, parent commit, binaries
ALTER TABLE repo_commits ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES repo_commits(id) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS repo_branches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id UUID NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  head_commit_id UUID REFERENCES repo_commits(id) ON DELETE SET NULL,
  UNIQUE (repo_id, lower(name))
);

ALTER TABLE repo_file_versions ADD COLUMN IF NOT EXISTS blob_attachment_id UUID REFERENCES attachments(id) ON DELETE SET NULL;


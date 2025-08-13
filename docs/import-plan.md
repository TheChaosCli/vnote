# Import Plan

Comprehensive import tools to accelerate adoption while preserving structure, tags, timestamps, and links.

## Supported Sources (MVP → Expanded)

- Markdown Folder: plain .md/.txt + frontmatter.
- Obsidian Vault: folder of Markdown, assets, wikilinks, frontmatter.
- Evernote .enex: notes, resources, tags, created/updated dates.
- Standard Notes JSON: decrypted export with items and tags.
- Joplin .jex (Expanded): tree, tags, resources, Markdown.

## Mapping Principles

- Preserve created_at/updated_at where available; add source_created/source_updated when conflicts.
- Map notebooks/folders to folders; tags to tags; links to links.
- Rewrite internal links to canonical note IDs/URLs; preserve broken links as plain text with warnings.
- Attachments: import as attachments with checksum dedupe; fix references in Markdown.
- Metadata: frontmatter → properties; unsupported keys kept in a catch‑all property.

## Pipelines

- Obsidian
  - Parse frontmatter (YAML) → properties.
  - Convert wikilinks [[Note]] and [[Note#Heading]] to internal links/anchors.
  - Embed handling: ![[image.png]] → attachment embeds.

- Evernote (.enex)
  - Parse ENML → Markdown; extract resources; map tags and dates.
  - Convert internal ENML links if resolvable; otherwise preserve as external links.

- Standard Notes (JSON)
  - Extract items of type note; map tags; Markdown or rich text body.
  - Preserve references/links if present.

- Joplin (.jex)
  - Walk tree; map folders, tags, resources; resolve link syntax.

## Import Engine

- Streaming parsers for large archives; back‑pressure and progress reporting.
- Deterministic IDs: content hash + path to enable resumable imports.
- Dry‑run mode: summarize changes; on commit, write in batches with rollback on failures.

## Tests & Fixtures

- Per‑source fixtures under /tests/importers with golden outputs.
- Verify tags, timestamps, internal links, attachments, and frontmatter mappings.


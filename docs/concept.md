# Concept: Modern, Self‑Hosted Note‑Taking Platform

This document captures the product vision, scope, and core experience for a secure, self‑hosted, local‑first note app inspired by Obsidian, Joplin, Standard Notes, Anytype, AppFlowy, Outline, and Trilium.

## Goals

- Privacy and ownership: all data lives on user‑controlled infrastructure.
- Local‑first UX: instant interactions, offline‑first, resilient sync.
- Powerful editor: Markdown + rich text, block model, media, math, tables, code.
- Networked knowledge: bidirectional links, backlinks, and an interactive graph.
- Scalable structure: folders, tags, properties, databases, and flexible views.
- Safe by default: version history, backups, and import paths from popular apps.

## Core Features

- Data & Editing
  - Local‑First & Self‑Hosted: PostgreSQL/MariaDB with attachments storage.
  - Editor: Markdown and WYSIWYG, tables, code blocks with syntax highlighting, math (KaTeX), images/audio/video attachments.
  - Block‑Based: granular blocks with drag‑and‑drop, embeds, and transforms.
  - Versioning: automatic versions with diff, restore, and audit trails.
  - Attachments: images, PDFs, audio/video with preview and metadata.

- Organization & Structure
  - Hierarchy: nested folders/spaces with per‑node permissions (future).
  - Links & Backlinks: bidirectional links, unlinked mentions, dead‑link checks.
  - Graph View: interactive graph filtered by tag/folder/time.
  - Tagging: fast tagging with filters, saved searches, and tag aliases.
  - Databases & Views: optional “properties on notes” with table, board, calendar, gallery views.

- Collaboration & Accessibility
  - Multi‑User: password‑based auth; per‑user data with shared spaces roadmap.
  - Real‑Time (optional): Yjs CRDT + y‑websocket for live cursors and edits.
  - Web App: React + Vite primary interface; responsive mobile web.
  - Mobile Apps (future): iOS/Android with offline cache and background sync.
  - Offline: Dexie/IndexedDB cache, deterministic merges on reconnect.

- Customization
  - Theming: light/dark and custom palettes; CSS variables.
  - Templates: reusable blocks and note templates with variables.

## Non‑Goals (Initial)

- Public publishing and anonymous sharing (consider later).
- Complex role‑based access across large teams (start single‑user; expand).
- Heavy automation/scripting engine (design extension points first).

## Success Metrics

- Cold start to first note < 60s in local dev.
- P95 editor interaction < 16 ms; initial load < 2s on typical hardware.
- Sync conflicts resolved deterministically with no data loss in test matrix.
- Importers preserve ≥ 95% of tags, timestamps, and links across fixtures.
- Backups and restores verified automatically via scripts.

## Personas

- Researcher/Writer: deep linking, citations, and long‑form editing.
- Engineer: code blocks, diagrams, checklists, and templates.
- Knowledge Manager: hierarchies, tags, databases, and views.

## MVP Scope

- Accounts: local password auth.
- Notes: create/read/update/delete; block editor with Markdown + WYSIWYG.
- Structure: folders, tags, backlinks; graph view (basic).
- Attachments: upload + preview; stored on disk or object storage.
- Versioning: per‑note snapshots with restore.
- Sync: single‑user offline cache; background push/pull; conflict policy.
- Import: Markdown folder + Obsidian vault (baseline), Evernote .enex (text + tags), Standard Notes JSON (baseline).
- Backups: scheduled DB + attachments backup; restore script.

## Open Questions

- Property model: per‑note flexible schema vs. typed “databases.”
- Collaboration tiering: which features belong to “advanced” mode.
- Graph scale: pruning and clustering strategies for large vaults.


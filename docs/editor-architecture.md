# Editor Architecture

Tiptap (ProseMirror)‑based editor with Markdown + rich text parity and a block model suitable for CRDT collaboration.

## Principles

- One source of truth: ProseMirror doc with stable block IDs.
- Markdown parity: round‑trip fidelity for common constructs.
- Extensible: custom nodes/marks for advanced blocks and embeds.
- Performant: minimal reflow, virtualized long notes, input latency < 20ms.

## Building Blocks

- Nodes: paragraph, heading, bulletList/orderedList/listItem, blockquote, horizontalRule, codeBlock (lang), table (thead/tbody/row/cell), image, attachment, callout, mathBlock, divider, embed (link/card), todoItem/todoList.
- Marks: bold, italic, underline, code, link, strike, highlight, sub/sup.
- Decorations: search highlights, backlinks hover previews, unlinked mentions.

## Extensions

- Markdown: serialize/parse with CommonMark, plus GFM tables, footnotes, task lists, strikethrough.
- Code: syntax highlighting via Shiki or low‑overhead prism‑lite; language detection optional.
- Math: KaTeX rendering, inline and block.
- Attachments: upload handler, paste/drag‑drop, progress UI, and signed URL fetching.
- Slash Menu: block insertions, transforms, and templates.
- Command Palette: global actions and note navigation.

## Collaboration

- CRDT: Yjs document bound to ProseMirror; awareness for cursors and selections.
- Sync: y‑websocket optional; otherwise periodic state vector push/pull.
- Versioning: capture snapshots on save/checkpoints; store block_versions.

## Offline & Caching

- Dexie/IndexedDB mirrors notes, blocks, and attachments metadata.
- Optimistic edits; reconcile upon server confirmation.

## Accessibility & i18n

- ARIA roles for toolbar, menus; keyboard‑first controls.
- LTR/RTL support; locale‑aware date/number formatting.

## Integration Points

- Link Resolver: hover preview, backlink insertion, broken link detector.
- Templates: param prompts and variable interpolation.
- Export: Markdown and HTML export with assets bundling.


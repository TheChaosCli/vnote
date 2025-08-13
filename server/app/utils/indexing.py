from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .crdt import decode_prosemirror_text_from_update
from sqlalchemy import text


async def update_note_search(session: AsyncSession, note_id: str, title: str | None, excerpt: str | None, body: str | None):
    text_content = " ".join([x for x in [title or "", excerpt or "", body or ""] if x])
    # Persist plain_text to notes for rebuilds
    await session.execute(text("UPDATE notes SET plain_text=:pt WHERE id::text=:id"), {"pt": body or "", "id": note_id})
    up = text(
        """
        INSERT INTO note_search (note_id, content_tsv)
        VALUES (:id::uuid, to_tsvector('english', :txt))
        ON CONFLICT (note_id) DO UPDATE SET content_tsv = EXCLUDED.content_tsv
        """
    )
    await session.execute(up, {"id": note_id, "txt": text_content})


async def rebuild_note_plaintext_from_blocks(session: AsyncSession, note_id: str) -> str:
    # For each block in the note, fetch latest snapshot and decode text
    sql = text(
        """
        SELECT b.id::text AS id,
               (
                 SELECT v.ydoc_snapshot FROM block_versions v WHERE v.block_id=b.id ORDER BY v.version DESC LIMIT 1
               ) AS snap
        FROM blocks b
        WHERE b.note_id::text=:nid
        ORDER BY b.order_idx
        """
    )
    res = await session.execute(sql, {"nid": note_id})
    body_parts: list[str] = []
    for r in res:
        snap = r.snap
        if snap:
            text_part = decode_prosemirror_text_from_update(bytes(snap))
            if text_part:
                body_parts.append(text_part)
    return "\n".join(body_parts)


async def rebuild_and_update_search(session: AsyncSession, note_id: str) -> None:
    meta = await session.execute(text("SELECT title, excerpt FROM notes WHERE id::text=:id"), {"id": note_id})
    row = meta.fetchone()
    if row is None:
        return
    body = await rebuild_note_plaintext_from_blocks(session, note_id)
    await update_note_search(session, note_id, row.title, row.excerpt, body)

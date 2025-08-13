import re
from typing import Iterable, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def extract_wikilinks(text_body: str) -> List[str]:
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text_body or "")]


async def rebuild_links_for_note(session: AsyncSession, user_id: str, note_id: str, body: str | None, create_missing: bool = True):
    # Remove existing source links
    await session.execute(text("DELETE FROM links WHERE src_note_id::text=:id"), {"id": note_id})
    if not body:
        return
    titles = extract_wikilinks(body)
    if not titles:
        return
    # Find destination notes by exact title
    existing = await session.execute(
        text("SELECT id, title FROM notes WHERE user_id=:uid::uuid AND title = ANY(:titles)"),
        {"uid": user_id, "titles": titles},
    )
    title_to_id = {r.title: r.id for r in existing}
    for t in titles:
        dst = title_to_id.get(t)
        if not dst and create_missing:
            # Create placeholder note
            ins = await session.execute(
                text("INSERT INTO notes (user_id, title) VALUES (:uid::uuid, :title) RETURNING id"),
                {"uid": user_id, "title": t},
            )
            dst = ins.fetchone()[0]
            title_to_id[t] = dst
        if dst:
            await session.execute(
                text(
                    "INSERT INTO links (src_note_id, dst_note_id, label) VALUES (:src::uuid, :dst::uuid, :lbl)"
                ),
                {"src": note_id, "dst": str(dst), "lbl": t},
            )

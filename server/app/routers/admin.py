from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session

router = APIRouter()


@router.post("/reindex-search")
async def reindex_search(session: AsyncSession = Depends(get_session)):
    # Recompute note_search from current notes (title, excerpt, plain_text)
    await session.execute(text("DELETE FROM note_search"))
    await session.execute(
        text(
            """
            INSERT INTO note_search (note_id, content_tsv)
            SELECT n.id, to_tsvector('english', coalesce(n.title,'') || ' ' || coalesce(n.excerpt,'') || ' ' || coalesce(n.plain_text,''))
            FROM notes n WHERE n.deleted_at IS NULL
            """
        )
    )
    await session.commit()
    return {"ok": True}


from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import TagOut, TagCreate, TagUpdate
from ..db import get_session
from ..auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/", response_model=List[TagOut])
async def list_tags(
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        SELECT t.id, t.name, t.color,
          (SELECT count(*) FROM note_tags nt WHERE nt.tag_id = t.id) AS count
        FROM tags t
        WHERE t.user_id = :uid::uuid
        ORDER BY lower(t.name)
        """
    )
    res = await session.execute(q, {"uid": user.id})
    rows = res.fetchall()
    return [TagOut(id=r.id, name=r.name, color=r.color, count=r.count) for r in rows]


@router.post("/", response_model=TagOut)
async def create_tag(
    payload: TagCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        INSERT INTO tags (user_id, name, color)
        VALUES (:uid::uuid, :name, :color)
        RETURNING id, name, color
        """
    )
    try:
        res = await session.execute(q, {"uid": user.id, "name": payload.name, "color": payload.color})
        row = res.fetchone()
        await session.commit()
        return TagOut(id=row.id, name=row.name, color=row.color, count=0)
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Tag already exists")


@router.patch("/{tag_id}", response_model=TagOut)
async def update_tag(
    tag_id: str,
    payload: TagUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        UPDATE tags SET
          name = COALESCE(:name, name),
          color = COALESCE(:color, color)
        WHERE id::text = :id AND user_id = :uid::uuid
        RETURNING id, name, color
        """
    )
    res = await session.execute(
        q, {"name": payload.name, "color": payload.color, "id": tag_id, "uid": user.id}
    )
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    await session.commit()
    # recompute count
    c = await session.execute(text("SELECT count(*) AS c FROM note_tags WHERE tag_id::text=:id"), {"id": tag_id})
    count = c.scalar() or 0
    return TagOut(id=row.id, name=row.name, color=row.color, count=count)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    await session.execute(
        text("DELETE FROM note_tags WHERE tag_id::text=:id"), {"id": tag_id}
    )
    res = await session.execute(
        text("DELETE FROM tags WHERE id::text=:id AND user_id=:uid::uuid"),
        {"id": tag_id, "uid": user.id},
    )
    await session.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"deleted": True}

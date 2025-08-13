from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..auth import get_current_user, CurrentUser
from ..utils.indexing import rebuild_and_update_search

router = APIRouter()


@router.post("/notes/{note_id}/blocks")
async def create_block(
    note_id: str,
    type: str,
    attrs: dict | None = None,
    after: float | None = None,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    # Ensure note ownership
    own = await session.execute(text("SELECT 1 FROM notes WHERE id::text=:id AND user_id=:uid::uuid AND deleted_at IS NULL"), {"id": note_id, "uid": user.id})
    if own.fetchone() is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if after is None:
        res = await session.execute(text("SELECT COALESCE(MAX(order_idx),0) + 1 FROM blocks WHERE note_id::text=:id"), {"id": note_id})
        order_idx = float(res.scalar() or 1)
    else:
        order_idx = after + 1.0
    ins = await session.execute(text("INSERT INTO blocks (note_id, type, attrs, order_idx) VALUES (:nid::uuid, :type, :attrs, :ord) RETURNING id::text"), {"nid": note_id, "type": type, "attrs": attrs or {}, "ord": order_idx})
    row = ins.fetchone()
    await session.commit()
    return {"id": row[0], "type": type, "attrs": attrs or {}, "order": order_idx}


@router.patch("/blocks/{block_id}")
async def update_block(
    block_id: str,
    attrs: dict | None = None,
    order: float | None = None,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        UPDATE blocks b SET
          attrs = COALESCE(:attrs, attrs),
          order_idx = COALESCE(:ord, order_idx),
          updated_at = now()
        WHERE b.id::text=:id AND EXISTS (
          SELECT 1 FROM notes n WHERE n.id=b.note_id AND n.user_id=:uid::uuid
        )
        RETURNING id::text
        """
    )
    res = await session.execute(q, {"attrs": attrs, "ord": order, "id": block_id, "uid": user.id})
    if res.fetchone() is None:
        raise HTTPException(status_code=404, detail="Block not found")
    await session.commit()
    return {"id": block_id, "updated": True}


@router.post("/blocks/{block_id}/crdt")
async def push_block_update(
    block_id: str,
    payload: bytes = Body(..., media_type="application/octet-stream"),
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    # Ensure ownership
    own = await session.execute(text("SELECT 1 FROM blocks b JOIN notes n ON n.id=b.note_id WHERE b.id::text=:id AND n.user_id=:uid::uuid"), {"id": block_id, "uid": user.id})
    if own.fetchone() is None:
        raise HTTPException(status_code=404, detail="Block not found")
    # Next version
    vres = await session.execute(text("SELECT COALESCE(MAX(version),0)+1 FROM block_versions WHERE block_id::text=:id"), {"id": block_id})
    version = int(vres.scalar() or 1)
    await session.execute(text("INSERT INTO block_versions (block_id, version, ydoc_snapshot) VALUES (:bid::uuid, :ver, :snap)"), {"bid": block_id, "ver": version, "snap": payload})
    # Rebuild note plaintext and update search index
    nid_res = await session.execute(text("SELECT note_id::text FROM blocks WHERE id::text=:id"), {"id": block_id})
    nid = nid_res.scalar()
    if nid:
        await rebuild_and_update_search(session, nid)
    await session.commit()
    return {"blockId": block_id, "version": version}

from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import Note, NoteCreate, Block
from ..db import get_session
from ..auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/", response_model=List[Note])
async def list_notes(
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    # Demo user scope
    q = text(
        """
        SELECT n.id, n.title, n.excerpt, n.folder_id, n.created_at, n.updated_at
        FROM notes n
        WHERE n.user_id = :uid::uuid AND n.deleted_at IS NULL
        ORDER BY n.updated_at DESC
        LIMIT 50
        """
    )
    res = await session.execute(q, {"uid": user.id})
    rows = res.fetchall()
    notes: List[Note] = []
    for r in rows:
        notes.append(
            Note(
                id=r.id,
                title=r.title,
                excerpt=r.excerpt,
                folderId=r.folder_id,
                createdAt=r.created_at,
                updatedAt=r.updated_at,
                blocks=[],
            )
        )
    return notes


@router.post("/", response_model=Note)
async def create_note(
    payload: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        INSERT INTO notes (user_id, title, folder_id)
        VALUES (:uid::uuid, :title, :folder_id)
        RETURNING id, title, excerpt, folder_id, created_at, updated_at
        """
    )
    res = await session.execute(
        q,
        {
            "uid": user.id,
            "title": payload.title,
            "folder_id": str(payload.folderId) if payload.folderId else None,
        },
    )
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Demo user not found; run seed")
    await session.commit()
    return Note(
        id=row.id,
        title=row.title,
        excerpt=row.excerpt,
        folderId=row.folder_id,
        createdAt=row.created_at,
        updatedAt=row.updated_at,
        blocks=[],
    )


@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: str,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        SELECT n.id, n.title, n.excerpt, n.folder_id, n.created_at, n.updated_at
        FROM notes n
        WHERE n.user_id = :uid::uuid AND n.id::text = :id
        """
    )
    res = await session.execute(q, {"uid": user.id, "id": note_id})
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return Note(
        id=row.id,
        title=row.title,
        excerpt=row.excerpt,
        folderId=row.folder_id,
        createdAt=row.created_at,
        updatedAt=row.updated_at,
        blocks=[],
    )


@router.patch("/{note_id}")
async def update_note(
    note_id: str,
    payload: dict,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")
    allowed = {k: v for k, v in payload.items() if k in {"title", "excerpt", "folderId"}}
    if not allowed:
        return {"id": note_id, "updated": {}}
    q = text(
        """
        UPDATE notes SET
          title = COALESCE(:title, title),
          excerpt = COALESCE(:excerpt, excerpt),
          folder_id = COALESCE(:folder_id, folder_id),
          updated_at = now()
        WHERE id::text = :id AND user_id = :uid::uuid
        RETURNING id, title, excerpt, folder_id, created_at, updated_at
        """
    )
    res = await session.execute(
        q,
        {
            "id": note_id,
            "title": allowed.get("title"),
            "excerpt": allowed.get("excerpt"),
            "folder_id": allowed.get("folderId"),
            "uid": user.id,
        },
    )
    row = res.fetchone()
    await session.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "id": str(row.id),
        "title": row.title,
        "excerpt": row.excerpt,
        "folderId": row.folder_id,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
    }


@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text("UPDATE notes SET deleted_at = now() WHERE id::text = :id AND user_id = :uid::uuid")
    await session.execute(q, {"id": note_id, "uid": user.id})
    await session.commit()
    return {"id": note_id, "deleted": True}

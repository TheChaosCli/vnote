import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..auth import get_current_user, CurrentUser
from ..storage import compute_checksum_and_save, resolve_path

router = APIRouter()


@router.post("/")
async def upload(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    dest = os.getenv("ATTACHMENTS_DIR", "/data/attachments")
    storage_key, checksum, size = compute_checksum_and_save(file.file, dest, file.filename)
    q = text(
        """
        INSERT INTO attachments (user_id, name, mime, bytes, checksum, storage_key, created_by)
        VALUES (:uid::uuid, :name, :mime, :bytes, :checksum, :storage_key, :uid::uuid)
        RETURNING id::text
        """
    )
    res = await session.execute(
        q,
        {
            "uid": user.id,
            "name": file.filename,
            "mime": file.content_type,
            "bytes": size,
            "checksum": checksum,
            "storage_key": storage_key,
        },
    )
    row = res.fetchone()
    await session.commit()
    return {"id": row[0], "name": file.filename, "mime": file.content_type, "bytes": size, "checksum": checksum}


@router.get("/{attachment_id}")
async def get_attachment(
    attachment_id: str,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        "SELECT storage_key, name, mime FROM attachments WHERE id::text=:id AND user_id=:uid::uuid"
    )
    res = await session.execute(q, {"id": attachment_id, "uid": user.id})
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Attachment not found")
    dest = os.getenv("ATTACHMENTS_DIR", "/data/attachments")
    path = resolve_path(dest, row.storage_key)
    if not os.path.exists(path):
        raise HTTPException(status_code=410, detail="Attachment missing")
    return {"id": attachment_id, "name": row.name, "mime": row.mime, "url": f"/attachments/{attachment_id}/download"}


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    res = await session.execute(
        text("SELECT storage_key, name, mime FROM attachments WHERE id::text=:id AND user_id=:uid::uuid"),
        {"id": attachment_id, "uid": user.id},
    )
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Attachment not found")
    dest = os.getenv("ATTACHMENTS_DIR", "/data/attachments")
    path = resolve_path(dest, row.storage_key)
    if not os.path.exists(path):
        raise HTTPException(status_code=410, detail="Attachment missing")
    return FileResponse(path, media_type=row.mime, filename=row.name)

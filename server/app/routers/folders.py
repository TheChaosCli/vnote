from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import Folder, FolderCreate, FolderUpdate
from ..db import get_session
from ..auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/tree")
async def get_tree(
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    # Fetch all folders for the user, then build a tree
    q = text(
        "SELECT id, name, parent_id FROM folders WHERE user_id=:uid::uuid ORDER BY name"
    )
    res = await session.execute(q, {"uid": user.id})
    rows = res.fetchall()
    nodes: Dict[str, Dict[str, Any]] = {}
    children: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        node = {"id": str(r.id), "name": r.name, "parentId": str(r.parent_id) if r.parent_id else None, "children": []}
        nodes[str(r.id)] = node
        if r.parent_id:
            children.setdefault(str(r.parent_id), []).append(node)
    roots = []
    for nid, node in nodes.items():
        pid = node["parentId"]
        if pid and pid in nodes:
            # parent will attach children by lookup later
            pass
        else:
            roots.append(node)
    for pid, kids in children.items():
        if pid in nodes:
            nodes[pid]["children"] = kids
    return {"roots": roots}


@router.post("/", response_model=Folder)
async def create_folder(
    payload: FolderCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        INSERT INTO folders (user_id, name, parent_id)
        VALUES (:uid::uuid, :name, :parent)
        RETURNING id, name, parent_id
        """
    )
    res = await session.execute(
        q, {"uid": user.id, "name": payload.name, "parent": str(payload.parentId) if payload.parentId else None}
    )
    row = res.fetchone()
    await session.commit()
    return Folder(id=row.id, name=row.name, parentId=row.parent_id)


@router.patch("/{folder_id}", response_model=Folder)
async def update_folder(
    folder_id: str,
    payload: FolderUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    q = text(
        """
        UPDATE folders SET
          name = COALESCE(:name, name),
          parent_id = COALESCE(:parent, parent_id),
          updated_at = now()
        WHERE id::text = :id AND user_id = :uid::uuid
        RETURNING id, name, parent_id
        """
    )
    res = await session.execute(
        q,
        {
            "name": payload.name,
            "parent": str(payload.parentId) if payload.parentId else None,
            "id": folder_id,
            "uid": user.id,
        },
    )
    row = res.fetchone()
    await session.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    return Folder(id=row.id, name=row.name, parentId=row.parent_id)


@router.delete("/{folder_id}")
async def delete_folder(
    folder_id: str,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    # Soft-delete notes in the folder could be added later. For now, reject delete if children exist.
    c = await session.execute(
        text("SELECT count(*) FROM folders WHERE parent_id::text=:id AND user_id=:uid::uuid"),
        {"id": folder_id, "uid": user.id},
    )
    if (c.scalar() or 0) > 0:
        raise HTTPException(status_code=400, detail="Folder not empty")
    res = await session.execute(
        text("DELETE FROM folders WHERE id::text=:id AND user_id=:uid::uuid"),
        {"id": folder_id, "uid": user.id},
    )
    await session.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"deleted": True}

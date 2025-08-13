from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("")
async def graph(
    scope: str | None = None,
    limit: int = 200,
    folderId: str | None = None,
    tag: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    filters = ["s.user_id = :uid::uuid", "d.user_id = :uid::uuid", "s.deleted_at IS NULL", "d.deleted_at IS NULL"]
    params = {"uid": user.id, "lim": limit}
    join_extra = ""
    if folderId:
        filters.append("(s.folder_id::text = :fid OR d.folder_id::text = :fid)")
        params["fid"] = folderId
    if tag:
        join_extra = "JOIN note_tags nts ON nts.note_id = s.id JOIN tags ts ON ts.id = nts.tag_id AND lower(ts.name)=lower(:tag) JOIN note_tags ntd ON ntd.note_id = d.id JOIN tags td ON td.id = ntd.tag_id AND lower(td.name)=lower(:tag)"
        params["tag"] = tag
    q = text(
        f"""
        SELECT l.src_note_id::text AS src, l.dst_note_id::text AS dst
        FROM links l
        JOIN notes s ON s.id = l.src_note_id
        JOIN notes d ON d.id = l.dst_note_id
        {join_extra}
        WHERE {' AND '.join(filters)}
        LIMIT :lim
        """
    )
    res = await session.execute(q, params)
    edges = [{"source": r.src, "target": r.dst} for r in res]
    ids = set()
    for e in edges:
        ids.add(e["source"])
        ids.add(e["target"])
    if not ids:
        return {"nodes": [], "edges": []}
    nodes_q = text(
        "SELECT id::text AS id, title FROM notes WHERE id = ANY(:ids)"
    )
    # SQLAlchemy needs array binding
    resn = await session.execute(nodes_q, {"ids": list(ids)})
    nodes = [{"id": r.id, "label": r.title} for r in resn]
    return {"nodes": nodes, "edges": edges}

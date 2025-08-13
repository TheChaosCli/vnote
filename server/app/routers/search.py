from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("")
async def search(
    q: str,
    folderId: str | None = None,
    tag: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    where = ["n.user_id = :uid::uuid", "n.deleted_at IS NULL"]
    params = {"q": q, "uid": user.id}
    if folderId:
        where.append("n.folder_id::text = :fid")
        params["fid"] = folderId
    join = ""
    if tag:
        join = "JOIN note_tags nt ON nt.note_id = n.id JOIN tags t ON t.id = nt.tag_id AND lower(t.name)=lower(:tag)"
        params["tag"] = tag
    query = text(
        f"""
        SELECT n.id::text AS id, n.title, n.excerpt,
               ts_rank(to_tsvector('english', coalesce(n.title,'') || ' ' || coalesce(n.excerpt,'')), plainto_tsquery('english', :q)) AS rank,
               ts_headline('english', coalesce(n.excerpt, n.title), plainto_tsquery('english', :q), 'StartSel=<b>,StopSel=</b>,MaxFragments=2,MinWords=5,MaxWords=20') AS snippet
        FROM notes n
        {join}
        WHERE {' AND '.join(where)}
          AND to_tsvector('english', coalesce(n.title,'') || ' ' || coalesce(n.excerpt,'')) @@ plainto_tsquery('english', :q)
        ORDER BY rank DESC, n.updated_at DESC
        LIMIT 50
        """
    )
    res = await session.execute(query, params)
    rows = res.mappings().all()
    return [{"id": r["id"], "title": r["title"], "excerpt": r["excerpt"], "snippet": r["snippet"], "rank": float(r["rank"] or 0)} for r in rows]

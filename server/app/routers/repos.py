import hashlib
import difflib
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/")
async def list_repos(session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    res = await session.execute(text("SELECT id::text AS id, name, created_at FROM repos WHERE user_id=:uid::uuid ORDER BY created_at DESC"), {"uid": user.id})
    return [{"id": r.id, "name": r.name, "createdAt": r.created_at} for r in res]


@router.post("/")
async def create_repo(name: str, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    try:
        res = await session.execute(text("INSERT INTO repos (user_id, name) VALUES (:uid::uuid, :name) RETURNING id::text"), {"uid": user.id, "name": name})
        row = res.fetchone()
        await session.commit()
        return {"id": row[0], "name": name}
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Repository exists")


@router.get("/{repo_id}/files")
async def list_files(repo_id: str, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    res = await session.execute(text("SELECT f.id::text AS id, f.path, f.updated_at FROM repo_files f JOIN repos r ON r.id=f.repo_id WHERE r.id::text=:rid AND r.user_id=:uid::uuid ORDER BY f.path"), {"rid": repo_id, "uid": user.id})
    return [{"id": r.id, "path": r.path, "updatedAt": r.updated_at} for r in res]


@router.get("/{repo_id}/files/{path:path}")
async def get_file(repo_id: str, path: str, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    q = text("""
        SELECT v.content
        FROM repo_files f
        JOIN repos r ON r.id=f.repo_id
        JOIN repo_file_versions v ON v.file_id=f.id
        JOIN repo_commits c ON c.id=v.commit_id
        WHERE r.id::text=:rid AND r.user_id=:uid::uuid AND f.path=:path
        ORDER BY c.created_at DESC
        LIMIT 1
    """)
    res = await session.execute(q, {"rid": repo_id, "uid": user.id, "path": path})
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"path": path, "content": row[0]}


@router.post("/{repo_id}/files")
async def upsert_file(repo_id: str, path: str, content: str | None = None, attachmentId: str | None = None, message: str = "update", session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    # Ensure repo
    ok = await session.execute(text("SELECT 1 FROM repos WHERE id::text=:rid AND user_id=:uid::uuid"), {"rid": repo_id, "uid": user.id})
    if ok.fetchone() is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    # Upsert file row
    res = await session.execute(text("""
        INSERT INTO repo_files (repo_id, path)
        VALUES (:rid::uuid, :path)
        ON CONFLICT (repo_id, path) DO UPDATE SET updated_at = now()
        RETURNING id::text
    """), {"rid": repo_id, "path": path})
    file_id = res.fetchone()[0]
    # Commit
    cres = await session.execute(text("INSERT INTO repo_commits (repo_id, message, author_id) VALUES (:rid::uuid, :msg, :uid::uuid) RETURNING id::text, created_at"), {"rid": repo_id, "msg": message, "uid": user.id})
    commit = cres.fetchone()
    commit_id = commit[0]
    if attachmentId is None and content is None:
        raise HTTPException(status_code=400, detail="content or attachmentId required")
    if attachmentId:
        checksum = "blob:" + attachmentId
        await session.execute(text("INSERT INTO repo_file_versions (file_id, commit_id, checksum, content, blob_attachment_id) VALUES (:fid::uuid, :cid::uuid, :cs, '', :aid::uuid)"), {"fid": file_id, "cid": commit_id, "cs": checksum, "aid": attachmentId})
    else:
        checksum = hashlib.sha256((content or "").encode("utf-8")).hexdigest()
        await session.execute(text("INSERT INTO repo_file_versions (file_id, commit_id, checksum, content) VALUES (:fid::uuid, :cid::uuid, :cs, :ct)"), {"fid": file_id, "cid": commit_id, "cs": checksum, "ct": content})
    await session.commit()
    return {"fileId": file_id, "commitId": commit_id}


@router.get("/{repo_id}/commits")
async def list_commits(repo_id: str, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    res = await session.execute(text("SELECT id::text AS id, message, created_at FROM repo_commits WHERE repo_id::text=:rid ORDER BY created_at DESC"), {"rid": repo_id})
    return [{"id": r.id, "message": r.message, "createdAt": r.created_at} for r in res]


@router.post("/{repo_id}/commit")
async def multi_file_commit(repo_id: str, message: str, files: List[dict], branch: str = "main", session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    # Ensure repo
    ok = await session.execute(text("SELECT 1 FROM repos WHERE id::text=:rid AND user_id=:uid::uuid"), {"rid": repo_id, "uid": user.id})
    if ok.fetchone() is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    # Branch
    b = await session.execute(text("SELECT id, head_commit_id FROM repo_branches WHERE repo_id::text=:rid AND lower(name)=lower(:name)"), {"rid": repo_id, "name": branch})
    br = b.fetchone()
    parent = br.head_commit_id if br else None
    # Create commit
    cres = await session.execute(text("INSERT INTO repo_commits (repo_id, message, author_id, parent_id) VALUES (:rid::uuid, :msg, :uid::uuid, :parent) RETURNING id::text"), {"rid": repo_id, "msg": message, "uid": user.id, "parent": parent})
    commit_id = cres.fetchone()[0]
    # Upsert files
    for f in files:
        path = f.get("path")
        content = f.get("content")
        attachment_id = f.get("attachmentId")
        if not path:
            continue
        res = await session.execute(text("INSERT INTO repo_files (repo_id, path) VALUES (:rid::uuid, :path) ON CONFLICT (repo_id, path) DO UPDATE SET updated_at = now() RETURNING id::text"), {"rid": repo_id, "path": path})
        file_id = res.fetchone()[0]
        if attachment_id:
            checksum = "blob:" + attachment_id
            await session.execute(text("INSERT INTO repo_file_versions (file_id, commit_id, checksum, content, blob_attachment_id) VALUES (:fid::uuid, :cid::uuid, :cs, '', :aid::uuid)"), {"fid": file_id, "cid": commit_id, "cs": checksum, "aid": attachment_id})
        else:
            checksum = hashlib.sha256((content or "").encode("utf-8")).hexdigest()
            await session.execute(text("INSERT INTO repo_file_versions (file_id, commit_id, checksum, content) VALUES (:fid::uuid, :cid::uuid, :cs, :ct)"), {"fid": file_id, "cid": commit_id, "cs": checksum, "ct": content or ""})
    # Update branch head
    if br:
        await session.execute(text("UPDATE repo_branches SET head_commit_id=:cid::uuid WHERE id=:bid"), {"cid": commit_id, "bid": br.id})
    else:
        await session.execute(text("INSERT INTO repo_branches (repo_id, name, head_commit_id) VALUES (:rid::uuid, :name, :cid::uuid)"), {"rid": repo_id, "name": branch, "cid": commit_id})
    await session.commit()
    return {"commitId": commit_id, "branch": branch}


@router.get("/{repo_id}/search")
async def repo_search(repo_id: str, q: str, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    # Search latest content per file by naive LIKE
    sql = text(
        """
        SELECT f.path, v.content
        FROM repo_files f
        JOIN LATERAL (
          SELECT v2.content FROM repo_file_versions v2 JOIN repo_commits c ON c.id=v2.commit_id WHERE v2.file_id=f.id ORDER BY c.created_at DESC LIMIT 1
        ) v ON true
        JOIN repos r ON r.id=f.repo_id
        WHERE r.id::text=:rid AND r.user_id=:uid::uuid AND v.content ILIKE :pat
        ORDER BY f.path
        LIMIT 200
        """
    )
    res = await session.execute(sql, {"rid": repo_id, "uid": user.id, "pat": f"%{q}%"})
    rows = res.fetchall()
    def lang_for(path: str) -> str:
        ext = (path.rsplit('.',1)[1] if '.' in path else '').lower()
        return {
            'py':'python','ts':'typescript','js':'javascript','tsx':'tsx','jsx':'jsx','java':'java','rb':'ruby','go':'go','rs':'rust','c':'c','h':'c','cpp':'cpp','hpp':'cpp','cs':'csharp','sh':'bash','md':'markdown','json':'json','yml':'yaml','yaml':'yaml'
        }.get(ext, 'text')
    results = []
    for r in rows:
        results.append({"path": r.path, "language": lang_for(r.path), "snippet": r.content[:400]})
    return results


@router.get("/{repo_id}/diff")
async def diff(repo_id: str, commitA: str, commitB: str, path: str, session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    # Fetch contents at each commit
    q = text("""
        SELECT va.content AS a, vb.content AS b
        FROM repo_files f
        JOIN repo_file_versions va ON va.file_id=f.id AND va.commit_id::text=:a
        JOIN repo_file_versions vb ON vb.file_id=f.id AND vb.commit_id::text=:b
        JOIN repos r ON r.id=f.repo_id
        WHERE r.id::text=:rid AND r.user_id=:uid::uuid AND f.path=:path
        LIMIT 1
    """)
    res = await session.execute(q, {"rid": repo_id, "uid": user.id, "path": path, "a": commitA, "b": commitB})
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No diff available")
    a, b = row[0].splitlines(keepends=False), row[1].splitlines(keepends=False)
    diff_lines = list(difflib.unified_diff(a, b, fromfile=commitA, tofile=commitB, lineterm=""))
    return {"path": path, "diff": diff_lines}

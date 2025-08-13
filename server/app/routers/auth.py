from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import AuthCredentials, AuthToken
from ..db import get_session
from ..auth import hash_password, verify_password, get_current_user, create_session_for_user, CurrentUser

router = APIRouter()


@router.post("/register", response_model=AuthToken)
async def register(creds: AuthCredentials, session: AsyncSession = Depends(get_session)):
    if not creds.email or not creds.password:
        raise HTTPException(status_code=400, detail="email and password required")
    # Check existence
    exists_q = text("SELECT 1 FROM users WHERE email=:email LIMIT 1")
    res = await session.execute(exists_q, {"email": creds.email})
    if res.fetchone() is not None:
        raise HTTPException(status_code=409, detail="email already registered")
    # Create user
    pw = hash_password(creds.password)
    ins_q = text(
        "INSERT INTO users (email, password_hash) VALUES (:email, :hash) RETURNING id::text"
    )
    res = await session.execute(ins_q, {"email": creds.email, "hash": pw})
    user_id = res.fetchone()[0]
    await session.commit()
    token = await create_session_for_user(user_id, session)
    return AuthToken(accessToken=token)


@router.post("/login", response_model=AuthToken)
async def login(creds: AuthCredentials, session: AsyncSession = Depends(get_session)):
    q = text("SELECT id::text, password_hash FROM users WHERE email=:email LIMIT 1")
    res = await session.execute(q, {"email": creds.email})
    row = res.fetchone()
    if row is None or not verify_password(row.password_hash, creds.password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = await create_session_for_user(row.id, session)
    return AuthToken(accessToken=token)


@router.post("/logout")
async def logout(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    creds = Depends(lambda: None),
):
    # Token revocation: delete caller's session by token
    # We can't easily access the token here without re-parsing; simplify by deleting all sessions for user
    q = text("DELETE FROM sessions WHERE user_id=:uid::uuid")
    await session.execute(q, {"uid": user.id})
    await session.commit()
    return {"ok": True}


@router.post("/refresh", response_model=AuthToken)
async def refresh(user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    token = await create_session_for_user(user.id, session)
    return AuthToken(accessToken=token)

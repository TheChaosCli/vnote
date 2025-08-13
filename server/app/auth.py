from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from argon2 import PasswordHasher

from .db import get_session


ph = PasswordHasher()
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hash_: str, password: str) -> bool:
    try:
        return ph.verify(hash_, password)
    except Exception:
        return False


@dataclass
class CurrentUser:
    id: str
    email: str


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> CurrentUser:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = creds.credentials
    q = text(
        """
        SELECT u.id::text AS id, u.email
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.id::text = :token AND (s.expires_at IS NULL OR s.expires_at > now())
        LIMIT 1
        """
    )
    res = await session.execute(q, {"token": token})
    row = res.fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return CurrentUser(id=row.id, email=row.email)


async def create_session_for_user(user_id: str, session: AsyncSession) -> str:
    token = secrets.token_hex(16)
    q = text(
        "INSERT INTO sessions (id, user_id, expires_at) VALUES (:id::uuid, :uid::uuid, now() + interval '7 days')"
    )
    # We store UUID format; if token isn't UUID, we can generate UUID in SQL
    # Instead, use gen_random_uuid() and return it
    q = text(
        "INSERT INTO sessions (user_id, expires_at) VALUES (:uid::uuid, now() + interval '7 days') RETURNING id::text"
    )
    res = await session.execute(q, {"uid": user_id})
    row = res.fetchone()
    await session.commit()
    return row[0]


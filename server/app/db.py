import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def _to_async_url(db_url: str) -> str:
    # Convert postgres:// to postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return db_url


DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://vnote:vnote@localhost:5432/vnote")
ASYNC_DB_URL = _to_async_url(DB_URL)

engine = create_async_engine(ASYNC_DB_URL, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


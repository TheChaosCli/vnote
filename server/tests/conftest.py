import os
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db import engine


async def _db_available() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    if not await _db_available():
        pytest.skip("DB not available; set DB_URL and run migrations to test")
    # Use a temp attachments dir for tests
    os.environ.setdefault("ATTACHMENTS_DIR", os.path.abspath("./.test-attachments"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


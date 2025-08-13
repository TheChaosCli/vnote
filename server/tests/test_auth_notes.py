import uuid
import pytest


async def register_and_login(client):
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    pwd = "pass1234"
    r = await client.post("/auth/register", json={"email": email, "password": pwd})
    assert r.status_code == 200
    token = r.json()["accessToken"]
    return token


@pytest.mark.anyio
async def test_auth_and_notes_flow(client):
    token = await register_and_login(client)
    # Create a note
    r = await client.post("/notes", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test", "body": "Hello [[Link]]"})
    assert r.status_code == 200
    note = r.json()
    assert note["title"] == "Test"
    # List notes
    r2 = await client.get("/notes", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    arr = r2.json()
    assert isinstance(arr, list)


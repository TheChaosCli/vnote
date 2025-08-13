import io
import pytest


@pytest.mark.anyio
async def test_tags_folders_attachments(client):
    # Register user
    tok = (await client.post("/auth/register", json={"email": "tagger@example.com", "password": "pass"})).json()["accessToken"]
    h = {"Authorization": f"Bearer {tok}"}
    # Tag
    r = await client.post("/tags", headers=h, json={"name": "inbox"})
    assert r.status_code in (200, 409)
    # Folder
    r = await client.post("/folders", headers=h, json={"name": "Docs"})
    assert r.status_code == 200
    # Attachment upload
    data = {"file": (io.BytesIO(b"hello"), "hello.txt")}
    r = await client.post("/attachments", headers=h, files=data)
    assert r.status_code == 200
    att = r.json()
    assert att["id"]


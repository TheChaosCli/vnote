from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/")
async def upload(file: UploadFile = File(...)):
    # Placeholder: do not persist
    return {"name": file.filename, "mime": file.content_type, "id": "stub"}


@router.get("/{attachment_id}")
def get_attachment(attachment_id: str):
    return {"id": attachment_id, "url": f"/attachments/{attachment_id}/download"}


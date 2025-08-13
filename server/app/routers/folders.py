from fastapi import APIRouter

router = APIRouter()


@router.get("/tree")
def get_tree():
    return {
        "id": "root",
        "name": "Root",
        "children": [
            {"id": "inbox", "name": "Inbox", "children": []},
        ],
    }


@router.post("/")
def create_folder(payload: dict):
    return {"id": "new", **payload}


from fastapi import APIRouter

router = APIRouter()


@router.get("")
def pull(since: str | None = None):
    return {"since": since, "changes": [], "tombstones": []}


@router.post("")
def push(batch: dict):
    return {"accepted": True, "count": len(batch) if isinstance(batch, list) else 1}


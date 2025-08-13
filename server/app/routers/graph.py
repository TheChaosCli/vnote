from fastapi import APIRouter

router = APIRouter()


@router.get("")
def graph(scope: str | None = None, limit: int = 200):
    return {
        "nodes": [
            {"id": "a", "label": "Welcome"},
            {"id": "b", "label": "Getting Started"},
        ],
        "edges": [{"source": "a", "target": "b"}],
        "scope": scope,
        "limit": limit,
    }


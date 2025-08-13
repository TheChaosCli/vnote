from uuid import uuid4
from typing import List
from fastapi import APIRouter
from ..schemas import Tag

router = APIRouter()


@router.get("/", response_model=List[Tag])
def list_tags():
    return [Tag(id=uuid4(), name="inbox"), Tag(id=uuid4(), name="todo", color="#f59e0b")]


@router.post("/")
def create_tag(tag: Tag):
    return tag


from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class NoteCreate(BaseModel):
    title: str
    folderId: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    properties: dict = Field(default_factory=dict)
    body: Optional[str] = None
    excerpt: Optional[str] = None


class Block(BaseModel):
    id: UUID
    type: str
    attrs: dict = Field(default_factory=dict)
    order: float


class Note(BaseModel):
    id: UUID
    title: str
    excerpt: Optional[str] = None
    folderId: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime
    blocks: List[Block] = Field(default_factory=list)
    body: Optional[str] = None


class AuthCredentials(BaseModel):
    email: str
    password: str


class AuthToken(BaseModel):
    accessToken: str
    tokenType: str = "bearer"


class Tag(BaseModel):
    id: UUID
    name: str
    color: Optional[str] = None


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagOut(Tag):
    count: int = 0


class Folder(BaseModel):
    id: UUID
    name: str
    parentId: Optional[UUID] = None


class FolderCreate(BaseModel):
    name: str
    parentId: Optional[UUID] = None


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    parentId: Optional[UUID] = None

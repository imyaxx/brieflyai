import uuid
from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_published: bool | None = None


class PostResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    summary: str | None
    is_published: bool
    author_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}

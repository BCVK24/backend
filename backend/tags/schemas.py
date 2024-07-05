from pydantic import BaseModel

from .models import TagDescription


class TagBase(BaseModel):
    pass


class TagRead(TagBase):
    id: int
    recording_id: int
    start: int
    end: int
    description: str


class TagUpdate(TagBase):
    id: int
    start: int
    end: int


class TagCreate(TagBase):
    recording_id: int
    start: int
    end: int
    description: TagDescription

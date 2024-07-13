from pydantic import BaseModel

from .models import TagDescription


class TagBase(BaseModel):
    start: float
    end: float
    class Config:
        use_enum_values = True


class TagRead(TagBase):
    id: int
    recording_id: int
    description: str

class TagUpdate(TagBase):
    id: int

class TagCreate(TagBase):
    recording_id: int
    description: TagDescription

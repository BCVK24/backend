from pydantic import BaseModel
from .models import TagType


class TagBase(BaseModel):
    start: float
    end: float
    description: str
    class Config:
        use_enum_values = True


class TagRead(TagBase):
    id: int
    recording_id: int
    tag_type: str


class TagUpdate(TagBase):
    id: int

class TagCreate(TagBase):
    recording_id: int
    description: str

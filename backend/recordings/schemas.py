import datetime as dt
from pydantic import BaseModel, AnyUrl


class RecordingBase(BaseModel):
    pass


class RecordingRead(RecordingBase):
    id: int
    created_at: dt.datetime
    creator_id: int
    title: str
    duration: int
    processing: bool


class RecordingCreate(RecordingBase):
    title: str

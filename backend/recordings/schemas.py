import datetime as dt
from pydantic import BaseModel, AnyUrl


class RecordingBase(BaseModel):
    creator_id: int


class RecordingRead(RecordingBase):
    id: int
    url: AnyUrl
    created_at: dt.datetime


class RecordingCreate(RecordingBase):
    pass

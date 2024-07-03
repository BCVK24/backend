import datetime as dt
from pydantic import BaseModel, AnyUrl


class RecordingBase(BaseModel):
    pass


class RecordingRead(RecordingBase):
    id: int
    url: AnyUrl
    created_at: dt.datetime
    creator_id: int


class RecordingCreate(RecordingBase):
    pass

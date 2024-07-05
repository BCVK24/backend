import datetime as dt
from pydantic import BaseModel, AnyUrl


class ResultBase(BaseModel):
    source_id: int


class ResultRead(ResultBase):
    id: int
    created_at: dt.datetime


class ResultCreate(ResultBase):
    pass

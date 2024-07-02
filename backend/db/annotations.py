import datetime as dt
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import mapped_column

from .database import get_session


intpk = Annotated[int, mapped_column(primary_key=True)]
dtnow = Annotated[dt.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


gen_session = Annotated[AsyncGenerator, Depends(get_session)]

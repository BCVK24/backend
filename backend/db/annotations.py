import datetime as dt
from typing import Annotated
from sqlalchemy import text
from sqlalchemy.orm import mapped_column


intpk = Annotated[int, mapped_column(primary_key=True)]
dtnow = Annotated[dt.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

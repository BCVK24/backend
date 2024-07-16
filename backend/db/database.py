from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import create_engine

from backend.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass

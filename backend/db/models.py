from datetime import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .annotations import intpk, dtnow


class TagDescription(enum.Enum):
    Silent = "SILENT"


class User(Base):
    __tablename__ = 'user'
    id: Mapped[intpk]

    recordings: Mapped[list['Recording']] = relationship(back_populates='creator', lazy='selectin')


class Result(Base):
    __tablename__ = 'result'
    id: Mapped[intpk]
    source_id: Mapped[int] = mapped_column(ForeignKey('recordings.id', ondelete='CASCADE'))
    url: Mapped[str]
    created_at: Mapped[dtnow]

    source: Mapped['Recording'] = relationship(back_populates='results', lazy='joined')


class Tag(Base):
    __tablename__ = 'tag'
    id: Mapped[intpk]
    recording_id: Mapped[int] = mapped_column(ForeignKey('recordings.id', ondelete='CASCADE'))
    start: Mapped[int]
    end: Mapped[int]
    description: Mapped[TagDescription]

    recording: Mapped['Recording'] = relationship(back_populates='tags', lazy='joined')

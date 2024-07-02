from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .enums import TagDescription
from .annotations import intpk, dtnow


class User(Base):
    __tablename__ = 'user'
    id: Mapped[intpk]

    recordings: Mapped[list['Recording']] = relationship(back_populates='creator', lazy='selectin')


class Recording(Base):
    __tablename__ = 'recording'
    id: Mapped[intpk]
    url: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    created_at: Mapped[dtnow]

    creator: Mapped['User'] = relationship(back_populates='recordings', lazy='joined')
    tags: Mapped[list['Tag']] = relationship(back_populates='recording', lazy='selectin')
    results: Mapped[list['Result']] = relationship(back_populates='source', lazy='selectin')


class Result(Base):
    __tablename__ = 'result'
    id: Mapped[intpk]
    source_id: Mapped[int] = mapped_column(ForeignKey('recording.id', ondelete='CASCADE'))
    url: Mapped[str]
    created_at: Mapped[dtnow]

    source: Mapped['Recording'] = relationship(back_populates='results', lazy='joined')


class Tag(Base):
    __tablename__ = 'tag'
    id: Mapped[intpk]
    recording_id: Mapped[int] = mapped_column(ForeignKey('recording.id', ondelete='CASCADE'))
    start: Mapped[int]
    end: Mapped[int]
    description: Mapped[TagDescription]

    recording: Mapped['Recording'] = relationship(back_populates='tags', lazy='joined')

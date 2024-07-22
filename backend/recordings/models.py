from ..db.database import Base
from ..db.crud import CRUD
from ..db.annotations import intpk, dtnow

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Recording(Base, CRUD):
    __tablename__ = 'recording'
    id: Mapped[intpk]
    url: Mapped[str]
    title: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    created_at: Mapped[dtnow]
    duration: Mapped[int]
    soundwave: Mapped[str]
    processing: Mapped[bool]

    creator: Mapped['User'] = relationship(
        back_populates='recordings', 
        lazy='joined'
    )
    tags: Mapped[list['Tag']] = relationship(
        back_populates='recording',
        lazy='selectin',
        cascade='all, delete-orphan'
    )
    display_tags: Mapped[list['Tag']] = relationship(
        back_populates='recording',
        lazy='selectin',
        cascade='all, delete-orphan',
        primaryjoin='and_(Recording.id == Tag.recording_id, Tag.tag_type != "SOURCETAG")'
    )
    results: Mapped[list['Result']] = relationship(
        back_populates='source', 
        lazy='selectin', 
        cascade='all, delete-orphan'
    )

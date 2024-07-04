import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.database import Base
from ..db.annotations import intpk


class TagDescription(enum.Enum):
    Silent = "SILENT"


class Tag(Base):
    __tablename__ = 'tag'
    id: Mapped[intpk]
    recording_id: Mapped[int] = mapped_column(ForeignKey('recordings.id', ondelete='CASCADE'))
    start: Mapped[int]
    end: Mapped[int]
    description: Mapped[TagDescription]

    recording: Mapped['Recording'] = relationship(back_populates='tags', lazy='joined')

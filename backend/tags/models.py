import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.database import Base
from ..db.crud import CRUD
from ..db.annotations import intpk


class TagType(enum.Enum):
    MODELTAG = "MODELTAG" # SPERMA
    USERTAG = "USERTAG" # PORNO
    SOURCETAG = "SOURCETAG" # V ROT GLUBOKO!!!!!!!!



class Tag(Base, CRUD):
    __tablename__ = 'tag'
    id: Mapped[intpk]
    recording_id: Mapped[int] = mapped_column(ForeignKey('recordings.id', ondelete='CASCADE'))
    start: Mapped[float]
    end: Mapped[float]
    description: Mapped[str]
    tag_type: Mapped[TagType]

    recording: Mapped['Recording'] = relationship(back_populates='tags', lazy='joined')

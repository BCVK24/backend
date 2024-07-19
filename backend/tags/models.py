import enum

from sqlalchemy import ForeignKey, delete, select
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

    recording: Mapped['Recording'] = relationship(back_populates='tags', lazy='joined', cascade='all, delete-orphan')

    @classmethod
    def delete_model_tag_by_recording_id(cls, recording_id):
        delete(Tag).where(cls.recording_id == recording_id and cls.tag_type == TagType.MODELTAG)

    @classmethod
    def get_source_tag_by_recording_id(cls, recording_id):
        query = (
            select(Tag).where(cls.recording_id == recording_id and cls.tag_type == TagType.SOURCETAG)
        )
        return query

import enum

from sqlalchemy import ForeignKey, delete, select, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.database import Base
from ..db.crud import CRUD
from ..db.annotations import intpk


class TagType(enum.Enum):
    MODELTAG = "MODELTAG" 
    USERTAG = "USERTAG"
    SOURCETAG = "SOURCETAG"



class Tag(Base, CRUD):
    __tablename__ = 'tag'
    id: Mapped[intpk]
    recording_id: Mapped[int] = mapped_column(ForeignKey('recording.id', ondelete='CASCADE'))
    start: Mapped[float]
    end: Mapped[float]
    description: Mapped[str]
    tag_type: Mapped[TagType]

    recording: Mapped['Recording'] = relationship(back_populates='tags', lazy='joined')

    @classmethod
    def delete_model_tag_by_recording_id(cls, recording_id):
        return delete(Tag).where(and_(cls.recording_id == recording_id, cls.tag_type == TagType.MODELTAG))

    @classmethod
    def get_source_tag_by_recording_id(cls, recording_id):
        return select(Tag).where(and_(cls.recording_id == recording_id, cls.tag_type == TagType.SOURCETAG))
        

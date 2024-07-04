from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.crud import CRUD
from ..db.database import Base
from ..db.annotations import intpk, dtnow
from ..db.crud import CRUD


class Result(Base, CRUD):
    __tablename__ = 'result'
    id: Mapped[intpk]
    source_id: Mapped[int] = mapped_column(ForeignKey('recordings.id', ondelete='CASCADE'))
    url: Mapped[str]
    created_at: Mapped[dtnow]

    source: Mapped['Recording'] = relationship(back_populates='results', lazy='joined')

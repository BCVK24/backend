from ..db.database import Base
from ..db.crud import CRUD
from ..db.annotations import intpk, dtnow

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Recording(Base, CRUD):
    __tablename__ = 'recordings'
    id: Mapped[intpk]
    url: Mapped[str]
    title: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    created_at: Mapped[dtnow]

    creator: Mapped['User'] = relationship(back_populates='recordings', lazy='joined')
    tags: Mapped[list['Tag']] = relationship(back_populates='recording', lazy='selectin')
    results: Mapped[list['Result']] = relationship(back_populates='source', lazy='selectin')

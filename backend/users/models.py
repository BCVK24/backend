from sqlalchemy.orm import Mapped, relationship

from ..db.crud import CRUD
from ..db.database import Base
from ..db.annotations import intpk


class User(Base, CRUD):
    __tablename__ = 'user'
    id: Mapped[intpk]
    # vk_id: Mapped[str]  # Hashed?

    recordings: Mapped[list['Recording']] = relationship(back_populates='creator', lazy='selectin')

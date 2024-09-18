from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from database.model_base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f'User({self.telegram_id=})'

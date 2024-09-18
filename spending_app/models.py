from sqlalchemy import String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.model_base import Base


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    amount = mapped_column(DECIMAL(10, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

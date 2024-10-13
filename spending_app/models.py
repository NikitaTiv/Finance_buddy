import decimal
from typing import List
from sqlalchemy import String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database.model_base import Base


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    user_id = mapped_column(ForeignKey('users.id'))

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")

    def __str__(self):
        return f'Category({self.name}, user={self.user_id})'


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    category_id = mapped_column(ForeignKey('category.id'))

    category: Mapped[Category] = relationship(back_populates="transactions")

    def __str__(self):
        return f'Transaction({self.amount}, category={self.category_id})'

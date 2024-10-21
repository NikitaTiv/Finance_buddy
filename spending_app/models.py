from datetime import datetime, timezone
import decimal
from typing import List
from sqlalchemy import DateTime, String, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database.model_base import Base


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    user_id = mapped_column(ForeignKey('users.id'))

    transactions: Mapped[List["Transaction"]] = relationship("Transaction", cascade="all, delete-orphan",
                                                             back_populates="category")

    def __str__(self) -> str:
        return f'Category({self.name}, user={self.user_id})'


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    category_id = mapped_column(ForeignKey('category.id'))

    category: Mapped[Category] = relationship("Category", back_populates="transactions")

    def __str__(self) -> str:
        return f'Transaction({self.amount}, category={self.category_id})'

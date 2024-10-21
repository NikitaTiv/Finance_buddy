from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

import buttons as bt
from database.engine import engine
from keyboards import BaseInlineKeyboard
from settings import MAX_CATEGORY_PER_USER
from keyboard_mixins import AddRemoveButtonMixin, GoBackHeaderMixin, NumbersMixin
from spending_app.models import Category


class CategoryInlineKeyboard(BaseInlineKeyboard):
    def __init__(self, user):
        super().__init__()
        self.user = user

    async def make_db_query(self) -> list[Any]:
        with Session(engine) as session:  # TODO async query
            return session.scalars(select(Category).where(Category.user_id == self.user.id)).all()

    @staticmethod
    def prepare_content(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [bt.InlineButton(text=row.name, callback_data=f'category_{row.id}') for row in results]


class RemoveCategoryInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    @staticmethod
    def prepare_content(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [bt.InlineButton(text=row.name, callback_data=f'remove_category_{row.id}') for row in results]


class CategoryInlineKeyboardWithAddAndRemove(AddRemoveButtonMixin, CategoryInlineKeyboard):
    @property
    def number_per_row(self) -> list[int]:
        return 0 < len(self.results) < MAX_CATEGORY_PER_USER and [2, 1] or [1,]


class CategoryGoBackInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    pass


class NumberInlineKeyboard(NumbersMixin, BaseInlineKeyboard):
    pass

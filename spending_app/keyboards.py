from typing import Any
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from sqlalchemy import select

import buttons as bt
from database.engine import engine
from spending_app.keyboard_mixins import AddRemoveButtonMixin, GoBackHeaderMixin
from spending_app.models import Category


start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [bt.ReplyButton(**bt.ADD_EXPENSES_BUTTON_DICT)],
], resize_keyboard=True)


class BaseInlineKeyboard:
    NUMBER_PER_ROW_QTY = (1,)

    def __init__(self):
        self.builder = InlineKeyboardBuilder()

    async def make_db_query(self):
        return []

    @staticmethod
    def prepare_headers(results):
        return []

    @staticmethod
    def prepare_content(results):
        return []

    def prepare_buttons_list(self, results):
        return self.prepare_headers(results) + self.prepare_content(results)

    def add_keyboard_buttons(self, buttons_list: list[dict[str, bool | str]]) -> None:
        for button in buttons_list:
            getattr(button, 'is_applicable') and self.builder.add(button)

    async def fill_builder(self) -> None:
        results = await self.make_db_query()
        buttons_list = self.prepare_buttons_list(results)
        self.add_keyboard_buttons(buttons_list)

    async def release_keyboard(self) -> Any:  # TODO
        await self.fill_builder()
        return self.builder.adjust(*self.NUMBER_PER_ROW_QTY).as_markup()

class CategoryInlineKeyboard(BaseInlineKeyboard):
    def __init__(self, user):
        super().__init__()
        self.user = user

    async def make_db_query(self):
        with Session(engine) as session:  # TODO async query
            return session.scalars(select(Category).where(Category.user_id == self.user.id)).all()

    @staticmethod
    def prepare_content(results):
        return [bt.InlineButton(text=row.name, callback_data=f'category_{row.id}') for row in results]


class CategoryInlineKeyboardWithAddAndRemove(AddRemoveButtonMixin, CategoryInlineKeyboard):
    NUMBER_PER_ROW_QTY = (2, 1)


class CategoryGoBackInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    pass


class GoBackInlineKeyboard(GoBackHeaderMixin, BaseInlineKeyboard):
    pass

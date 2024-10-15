from abc import ABC, abstractmethod
from typing import Any, Optional
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.orm import Session
from sqlalchemy import select

import buttons as bt
from database.engine import engine
from settings import MAX_CATEGORY_PER_USER
from spending_app.keyboard_mixins import AddRemoveButtonMixin, GoBackHeaderMixin, MainKeyboardMixin, NumbersMixin
from spending_app.models import Category


class BaseKeyboard(ABC):
    """
    Base class for creating keyboards.
    """
    def __init__(self):
        self.builder = self.get_builder()

    @abstractmethod
    def get_builder(self):
        """
        Inheritors must override the builder attribute.
        """
        pass

    @property
    def number_per_row(self) -> list[int]:
        """
        Allows to regulate the buttons quantity per rows.

        :return: List with number of elements per line.
        """
        return [1,]

    async def make_db_query(self) -> list[Optional[Any]]:
        """
        Receives elems from DB to form buttons.

        :return: List with db elements.
        """
        return []

    @staticmethod
    def prepare_headers(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        """
        Create header's buttons for a buttons panel.

        :param results: List with db elements.
        :return: List of button instances.
        """
        return []

    @staticmethod
    def prepare_content(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        """
        Create body's buttons for a buttons panel.

        :param results: List with db elements.
        :return: List of button instances.
        """
        return []

    def prepare_buttons_list(self, results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        """
        Combine headers and body lists of buttons.

        :param results: List with db elements.
        :return: List of button instances.
        """
        return self.prepare_headers(results) + self.prepare_content(results)

    def add_keyboard_buttons(self, buttons_list: list[bt.InlineButton | bt.ReplyButton | None]) -> None:
        """
        Add buttons to the builder.

        :param buttons_list: List of button instances.
        """
        for button in buttons_list:
            getattr(button, 'is_applicable') and self.builder.add(button)

    async def fill_builder(self) -> None:
        """
        Method manager in which commands are launched to prepare the builder.
        """
        self.results = await self.make_db_query()
        buttons_list = self.prepare_buttons_list(self.results)
        self.add_keyboard_buttons(buttons_list)

    async def release_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
        """
        Returns a prepared builder obj to a handler.

        :return: A keyboard object.
        """
        await self.fill_builder()
        return self.builder.adjust(*self.number_per_row).as_markup()


class BaseInlineKeyboard(BaseKeyboard):
    def get_builder(self):
        return InlineKeyboardBuilder()


class BaseReplyKeyboard(BaseKeyboard):
    RESIZE_KEYBOARD = True

    def get_builder(self):
        return ReplyKeyboardBuilder()

    async def release_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
        await self.fill_builder()
        return self.builder.adjust(*self.number_per_row).as_markup(resize_keyboard=self.RESIZE_KEYBOARD)


class CategoryInlineKeyboard(BaseInlineKeyboard):
    def __init__(self, user):
        super().__init__()
        self.user = user

    async def make_db_query(self) -> list[Optional[Any]]:
        with Session(engine) as session:  # TODO async query
            return session.scalars(select(Category).where(Category.user_id == self.user.id)).all()

    @staticmethod
    def prepare_content(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [bt.InlineButton(text=row.name, callback_data=f'category_{row.id}') for row in results]


class RemoveCategoryInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    @staticmethod
    def prepare_content(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [bt.InlineButton(text=row.name, callback_data=f'remove_category_{row.id}') for row in results]


class CategoryInlineKeyboardWithAddAndRemove(AddRemoveButtonMixin, CategoryInlineKeyboard):
    @property
    def number_per_row(self) -> list[int]:
        return 0 < len(self.results) < MAX_CATEGORY_PER_USER and [2, 1] or [1,]


class CategoryGoBackInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    pass


class GoBackInlineKeyboard(GoBackHeaderMixin, BaseInlineKeyboard):
    pass


class NumberInlineKeyboard(NumbersMixin, BaseInlineKeyboard):
    pass

class MainReplyKeyboard(MainKeyboardMixin, BaseReplyKeyboard):
    pass

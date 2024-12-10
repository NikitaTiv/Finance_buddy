from abc import ABC, abstractmethod
from itertools import chain
from sqlalchemy.orm.query import Query
from typing import Any, Generator, Iterable, Optional

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import buttons_base as bt
from keyboard_mixins import GoBackHeaderMixin, MainKeyboardMixin


class BaseKeyboard(ABC):
    """
    Base class for creating keyboards.
    """
    def __init__(self) -> None:
        self.builder = self.get_builder()

    @abstractmethod
    def get_builder(self) -> InlineKeyboardBuilder | ReplyKeyboardBuilder:
        """
        Inheritors must override the builder attribute.
        """
        pass

    @property
    def number_per_row(self) -> tuple[int]:
        """
        Allows to regulate the buttons quantity per rows.

        :return: List with number of elements per line.
        """
        return (1,)

    async def make_db_query(self) -> Optional[Query]:
        """
        Receives elems from DB to form buttons.

        :return: List with db elements.
        """
        pass

    def get_results_qty(self, query_obj: Query) -> int:
        """
        The method checks whether the object has the results_qty attribute,
        if it does not, it makes a request to the database and creates.

        :param query_obj: SQL Alchemy query object.
        :return: Number of elements in the database.
        """
        if not (results_qty := getattr(self, 'results_qty', None)):
            self.results_qty = query_obj.count()
            return self.results_qty
        return results_qty

    def prepare_headers(self, db_query: Optional[Query]) -> \
        Iterable[bt.InlineButton | bt.ReplyButton] | Generator[bt.InlineButton | bt.ReplyButton, None, None]:
        """
        Create header's buttons for a buttons panel.

        :param results: SQL Alchemy query object.
        :return: List of button instances.
        """
        yield from ()

    def prepare_content(self, db_query: Optional[Query]) -> \
        Iterable[bt.InlineButton | bt.ReplyButton] | Generator[bt.InlineButton | bt.ReplyButton, None, None]:
        """
        Create body's buttons for a buttons panel.

        :param results: SQL Alchemy query object.
        :return: List of button instances.
        """
        yield from ()

    def prepare_footer(self, db_query: Optional[Query]) -> \
        Iterable[bt.InlineButton | bt.ReplyButton] | Generator[bt.InlineButton | bt.ReplyButton, None, None]:
        """
        Create footer's buttons for a buttons panel.

        :param results: SQL Alchemy query object.
        :return: List of button instances.
        """
        yield from ()

    def prepare_buttons_list(self, db_query: Optional[Query]) \
        -> chain[Iterable[bt.InlineButton | bt.ReplyButton] |
                 Generator[bt.InlineButton | bt.ReplyButton, None, None]]:
        """
        Combine headers, body and footer lists of buttons.

        :param results: SQL Alchemy query object.
        :return: List of button instances.
        """
        return chain(self.prepare_headers(db_query),
                     self.prepare_content(db_query),
                     self.prepare_footer(db_query))

    def add_keyboard_buttons(self, buttons_gen: chain[Iterable[bt.InlineButton | bt.ReplyButton] |
                                                      Generator[bt.InlineButton | bt.ReplyButton, None, None]]) -> None:
        """
        Add buttons to the builder.

        :param buttons_list: List of button instances.
        """
        for button in buttons_gen:
            getattr(button, 'is_applicable') and self.builder.add(button)

    async def fill_builder(self) -> None:
        """
        Method manager in which commands are launched to prepare the builder.
        """
        self.db_query = await self.make_db_query()
        buttons_gen = self.prepare_buttons_list(self.db_query)
        self.add_keyboard_buttons(buttons_gen)

    async def release_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
        """
        Returns a prepared builder obj to a handler.

        :return: A keyboard object.
        """
        await self.fill_builder()
        return self.builder.adjust(*self.number_per_row).as_markup()


class BaseInlineKeyboard(BaseKeyboard):
    def get_builder(self) -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()


class BaseReplyKeyboard(BaseKeyboard):
    RESIZE_KEYBOARD = True

    def get_builder(self) -> ReplyKeyboardBuilder:
        return ReplyKeyboardBuilder()

    async def release_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
        await self.fill_builder()
        return self.builder.adjust(*self.number_per_row).as_markup(resize_keyboard=self.RESIZE_KEYBOARD)


class MainReplyKeyboard(MainKeyboardMixin, BaseReplyKeyboard):
    pass


class GoBackInlineKeyboard(GoBackHeaderMixin, BaseInlineKeyboard):
    pass

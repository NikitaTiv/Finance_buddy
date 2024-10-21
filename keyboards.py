from abc import ABC, abstractmethod
from typing import Any
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


import buttons as bt
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
    def number_per_row(self) -> list[int]:
        """
        Allows to regulate the buttons quantity per rows.

        :return: List with number of elements per line.
        """
        return [1,]

    async def make_db_query(self) -> list[Any]:
        """
        Receives elems from DB to form buttons.

        :return: List with db elements.
        """
        return []

    @staticmethod
    def prepare_headers(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        """
        Create header's buttons for a buttons panel.

        :param results: List with db elements.
        :return: List of button instances.
        """
        return []

    @staticmethod
    def prepare_content(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        """
        Create body's buttons for a buttons panel.

        :param results: List with db elements.
        :return: List of button instances.
        """
        return []

    def prepare_buttons_list(self, results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        """
        Combine headers and body lists of buttons.

        :param results: List with db elements.
        :return: List of button instances.
        """
        return self.prepare_headers(results) + self.prepare_content(results)

    def add_keyboard_buttons(self, buttons_list: list[bt.InlineButton | bt.ReplyButton]) -> None:
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

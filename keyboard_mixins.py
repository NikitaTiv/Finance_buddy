from typing import Any
from report_app.buttons_dataclasses import GetReportButtonData
from spending_app.buttons_dataclasses import (AddCategoryButtonData, AddExpensesButtonData, BackButtonButtonData,
                                              RemoveCategoryButtonData)
from spending_app.filters import ReturnCallback

import buttons_base as bt
from settings import MAX_CATEGORY_PER_USER


class GoBackHeaderMixin:
    @staticmethod
    def prepare_headers(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [
            bt.InlineButton(text=BackButtonButtonData.text,
                            callback_data=ReturnCallback(direction=BackButtonButtonData.callback_data).pack())
        ]


class AddRemoveButtonMixin:
    @staticmethod
    def prepare_headers(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [bt.InlineButton(is_applicable=len(results) < MAX_CATEGORY_PER_USER,
                                **AddCategoryButtonData.get_attrs()),
                bt.InlineButton(is_applicable=bool(results), **RemoveCategoryButtonData.get_attrs())]


class NumbersMixin:
    @property
    def number_per_row(self) -> list[int]:
        return [3,]

    @staticmethod
    def prepare_content(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        number_buttons = [bt.InlineButton(text=str(number), callback_data=f'amount_category_{number}')
                          for number in range(1, 10)]
        footer_buttons = [
            bt.InlineButton(text='⬅️', callback_data=ReturnCallback(
                direction=BackButtonButtonData.callback_data).pack()),
            bt.InlineButton(text=str(0), callback_data='amount_category_0'),
            bt.InlineButton(text='OK', callback_data='amount_category_OK'),
        ]
        return number_buttons + footer_buttons


class MainKeyboardMixin:
    @staticmethod
    def prepare_content(results: list[Any]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [
            bt.ReplyButton(**AddExpensesButtonData.get_attrs()),
            bt.ReplyButton(**GetReportButtonData.get_attrs()),
        ]

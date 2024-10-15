from typing import Any, Optional
from spending_app.filters import ReturnCallback

import buttons as bt
from settings import MAX_CATEGORY_PER_USER


class GoBackHeaderMixin:
    @staticmethod
    def prepare_headers(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [
            bt.InlineButton(text=bt.BACK_BUTTON_DICT.get('text'),
                            callback_data=ReturnCallback(direction=bt.BACK_BUTTON_DICT.get('callback_data')).pack())
        ]


class AddRemoveButtonMixin:
    @staticmethod
    def prepare_headers(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [bt.InlineButton(is_applicable=len(results) < MAX_CATEGORY_PER_USER, **bt.ADD_CATEGORY_BUTTON_DICT),
                bt.InlineButton(is_applicable=bool(results), **bt.REMOVE_CATEGORY_BUTTON_DICT)]


class NumbersMixin:
    @property
    def number_per_row(self) -> list[int]:
        return [3,]

    @staticmethod
    def prepare_content(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        number_buttons = [bt.InlineButton(text=str(number), callback_data=f'amount_category_{number}')
                          for number in range(1, 10)]
        footer_buttons = [
            bt.InlineButton(text='⬅️', callback_data=ReturnCallback(direction=bt.BACK_BUTTON_DICT
                                                                    .get('callback_data')).pack()),
            bt.InlineButton(text=str(0), callback_data='amount_category_0'),
            bt.InlineButton(text='OK', callback_data='amount_category_OK'),
        ]
        return number_buttons + footer_buttons


class MainKeyboardMixin:
    @staticmethod
    def prepare_content(results: list[Optional[Any]]) -> list[bt.InlineButton | bt.ReplyButton | None]:
        return [
            bt.ReplyButton(**bt.ADD_EXPENSES_BUTTON_DICT),
            bt.ReplyButton(**bt.GET_REPORT_BUTTON_DICT),
        ]

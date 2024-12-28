from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ReturnCallback(CallbackData, prefix="back"):
    direction: Optional[str]


class ShowNextCallback(CallbackData, prefix="show_next"):
    direction: Optional[str]


class ShowPrevCallback(CallbackData, prefix="show_prev"):
    direction: Optional[str]


class LimitCallback(CallbackData, prefix="limit"):
    direction: Optional[str]


class EditLimitCallback(CallbackData, prefix="edit_limit"):
    direction: Optional[str]


class RemoveLimitCallback(CallbackData, prefix="remove_limit"):
    direction: Optional[str]

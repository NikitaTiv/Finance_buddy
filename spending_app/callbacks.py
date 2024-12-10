from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ReturnCallback(CallbackData, prefix="back"):
    """
    Class for creating GoBack callbacks.
    """
    direction: Optional[str]


class ShowNextCallback(CallbackData, prefix="show_next"):
    """
    Class for creating GoBack callbacks.
    """
    direction: Optional[str]


class ShowPrevCallback(CallbackData, prefix="show_prev"):
    """
    Class for creating GoBack callbacks.
    """
    direction: Optional[str]

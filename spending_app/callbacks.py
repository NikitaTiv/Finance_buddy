from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ReturnCallback(CallbackData, prefix="back"):
    """
    Class for creating GoBack callbacks.
    """
    direction: Optional[str]

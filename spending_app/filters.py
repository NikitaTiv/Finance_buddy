import re
from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message

import buttons as bt


class ReturnCallback(CallbackData, prefix="back"):
    """
    Class for creating GoBack callbacks.
    """
    direction: Optional[str]


class ChooseCategoryMessageFilter(BaseFilter):
    """
    Class for catching expenses's events.
    """
    async def __call__(self, message: Message) -> bool:
        return (message.text == bt.ADD_EXPENSES_BUTTON_DICT.get('text')
                or bool(re.search(r'Категория .+ успешно добавлена|удалена.', getattr(message, 'text', ''))))

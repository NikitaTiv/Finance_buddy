import re

from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message

import buttons as bt


class ReturnCallback(CallbackData, prefix="back"):
    direction: str


class MainPageFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text.lower() == '/start'


class ChooseCategoryMessageFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return (message.text == bt.ADD_EXPENSES_BUTTON_DICT.get('text')
                or re.search(r'Категория .+ успешно добавлена|удалена.', message.text))




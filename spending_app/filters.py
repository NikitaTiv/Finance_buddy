from aiogram.filters import BaseFilter
from aiogram.types import Message


class MainPageFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text.lower() == '/start' or message.text.endswith('На главную')

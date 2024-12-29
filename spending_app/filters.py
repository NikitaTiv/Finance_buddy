import re
from aiogram import types
from aiogram.filters.base import Filter

from spending_app.callbacks import RemoveTransactionCallback


class RemoveTransactionFilter(Filter):
    async def __call__(self, callback: types.CallbackQuery) -> bool:
        pattern = rf"^{RemoveTransactionCallback.__prefix__}:\d+_(yes|no)$"
        return bool(re.match(pattern, callback.data))

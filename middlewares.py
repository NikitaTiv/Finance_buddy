from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class UserRequiredMiddleware(BaseMiddleware):
    """
    No need to handle requests without a user
    """
    async def __call__(self,
                       handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: dict[str, Any]) -> Any:
        if isinstance(event, (Message, CallbackQuery)) and not getattr(event.from_user, 'id'):
            return
        return await handler(event, data)

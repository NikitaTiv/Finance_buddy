from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import TelegramMethod
from aiogram.methods.base import Response, TelegramType


class SkipTelegramBadRequestSession(AiohttpSession):
    """
    We have cases when we respond with the same message,
    for this reason we would like to skip the 'TelegramBadRequest: message is not modified' error.
    """
    def check_response(self, bot: Bot, method: TelegramMethod[TelegramType],
                       status_code: int, content: str) -> Response[TelegramType]:
        try:
            return super().check_response(bot, method, status_code, content)
        except TelegramBadRequest:
            json_data = self.json_loads(content)
            response_type = Response[method.__returning__]  # type: ignore
            return response_type.model_validate(json_data, context={"bot": bot})

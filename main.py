import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.engine import engine
from database.model_base import Base
from spending_app.handlers import spending_router
from spending_app.models import *  # for creating tables

dp = Dispatcher()

load_dotenv()


async def main() -> None:
    bot = Bot(token=os.environ.get('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(spending_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

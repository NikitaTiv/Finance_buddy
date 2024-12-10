import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
import sentry_sdk
from sqlalchemy.orm import Session

from database.engine import engine
from database.model_base import Base
import keyboards as kb
from rewritten_base_classes import ClearCacheDispatcher
from settings import SENTRY_TOKEN
from spending_app.handlers import spending_router
from report_app.handlers import report_router
from middlewares import UserRequiredMiddleware
from spending_app.models import *  # noqa: F401, F403
from users_app.models import User


load_dotenv()

sentry_sdk.init(
    dsn=SENTRY_TOKEN,
    traces_sample_rate=1.0,
)

dp: Dispatcher = ClearCacheDispatcher()

dp.message.middleware(UserRequiredMiddleware())
dp.callback_query.middleware(UserRequiredMiddleware())


@dp.message(CommandStart())
async def start_conversation(message: Message) -> None:
    user_id = message.from_user.id
    with Session(engine) as session:  # TODO create a async context manager for adding users
        if not session.query(User).filter(User.telegram_id == user_id).count():
            user = User(telegram_id=user_id)
            session.add(user)
            session.commit()
    await message.answer('Привет, это твой Finance buddy',
                         reply_markup=await kb.MainReplyKeyboard().release_keyboard())


async def main() -> None:
    bot = Bot(token=os.environ.get('TOKEN'))
    dp.include_routers(spending_router, report_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    sentry_sdk.profiler.start_profiler()
    asyncio.run(main())
    sentry_sdk.profiler.stop_profiler()

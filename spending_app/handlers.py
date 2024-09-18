from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from sqlalchemy.orm import Session

from database.engine import engine
from spending_app.filters import MainPageFilter
import spending_app.keyboards as kb
from users_app.models import User


spending_router = Router()


@spending_router.message(MainPageFilter())
async def start_conversation(message: Message) -> None:
    user_id = message.from_user.id
    with Session(engine) as session:  # TODO create a async function for adding users
        if not session.query(User).filter(User.telegram_id == user_id).count():
            user = User(telegram_id=user_id)
            session.add(user)
            session.commit()
    await message.answer('Привет, это твой Finance buddy', reply_markup=kb.start_keyboard)


@spending_router.message(F.text == 'Добавить расходы')
async def choose_category(message: Message) -> None:
    await message.answer('Выберите или создайте категорию (максимум 8)',
                         reply_markup=await kb.create_category_keyboard())

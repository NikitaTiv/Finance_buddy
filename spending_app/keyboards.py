from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.engine import engine
from spending_app.models import Category
from spending_app.utils import add_keyboard_button


start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить расходы')],
], resize_keyboard=True)


async def create_category_keyboard(user_id) -> None:
    with Session(engine) as session:
        results = session.scalars(select(Category).where(Category.user_id == user_id)).all()
    category_keyboard = ReplyKeyboardBuilder()
    add_keyboard_button(({'is_applicable': len(results) < 8, 'text': '➕ Добавить категорию'},
                         {'is_applicable': bool(results), 'text': '❌ Удалить категорию'}), category_keyboard)
    for row in results:
        category_keyboard.button(text=row.name)
    category_keyboard.button(text='⬅️ На главную')
    return category_keyboard.adjust(2).as_markup()

# stmt = insert(Category).values(name='Мясо', user_id=user_id)
# session.execute(stmt)
# session.commit()

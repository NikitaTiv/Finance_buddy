from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить расходы')]
], )

async def create_category_keyboard() -> None:
    category_keyboard = ReplyKeyboardBuilder()
    for _ in range(6):
        category_keyboard.button(text='➕ Add category')
    category_keyboard.button(text='⬅️ На главную')
    return category_keyboard.adjust(2).as_markup()  # TODO make authomatic adjust

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить расходы')],
], resize_keyboard=True)

async def create_category_keyboard() -> None:
    category_keyboard = ReplyKeyboardBuilder()
    category_keyboard.add(KeyboardButton(text='➕ Добавить категорию'),
                          KeyboardButton(text='❌ Удалить категорию'))
    for _ in range(0):
        category_keyboard.button(text='Моя категория')
    category_keyboard.button(text='⬅️ На главную')
    return category_keyboard.adjust(2).as_markup()

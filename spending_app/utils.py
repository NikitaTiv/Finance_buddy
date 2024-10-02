from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def add_keyboard_button(content: tuple[dict[str, bool | str]], keyboard: ReplyKeyboardBuilder) -> None:
    for elem in content:
        elem['is_applicable'] and keyboard.add(KeyboardButton(text=elem['text']))

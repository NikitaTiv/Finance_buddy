import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import insert
from sqlalchemy.orm import Session
from aiogram.fsm.context import FSMContext

import buttons as bt
from database.engine import engine
import keyboards as main_kb
from spending_app.consts import ALLOWED_CATEGORY_LENGHT, GREETING_SPEND_APP_MESSAGE
from spending_app.filters import ReturnCallback, ChooseCategoryMessageFilter
import spending_app.keyboards as spend_kb
from spending_app.models import Category, Transaction
from spending_app.state_groups import CategoryGroup, TransactionGroup


spending_router = Router()


@spending_router.callback_query(ReturnCallback.filter(F.direction == "cat"))
@spending_router.message(ChooseCategoryMessageFilter())
async def choose_category(request: Message | CallbackQuery) -> None:
    method = isinstance(request, Message) and request.answer or (await request.answer() and request.message.edit_text)
    await method(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                 spend_kb.CategoryInlineKeyboardWithAddAndRemove(request.from_user).release_keyboard())


@spending_router.callback_query(F.data == bt.REMOVE_CATEGORY_BUTTON_DICT.get('callback_data'))
async def select_category_for_removal(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text('Выберите категорию для удаления.',
                                     reply_markup=await
                                     spend_kb.RemoveCategoryInlineKeyboard(callback.from_user).release_keyboard())


@spending_router.callback_query(F.data.startswith('remove_category_'))
async def remove_category(callback: CallbackQuery) -> None:
    with Session(engine) as session:
        obj = session.query(Category).filter(Category.id == callback.data.split('_')[2],
                                             Category.user_id == callback.from_user.id).first()
        session.delete(obj)
        session.commit()
    await callback.answer('Категория удалена.')
    await callback.message.edit_text(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                                     spend_kb.CategoryInlineKeyboardWithAddAndRemove(callback.from_user).
                                     release_keyboard())


@spending_router.callback_query(F.data == bt.ADD_CATEGORY_BUTTON_DICT.get('callback_data'))
async def add_category(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CategoryGroup.category_name)
    await callback.answer()
    await callback.message.edit_text('Введите имя категории.',
                                     reply_markup=await main_kb.GoBackInlineKeyboard().release_keyboard())


@spending_router.message(CategoryGroup.category_name)
async def get_category_name(message: Message, state: FSMContext) -> None:
    if len(category_name := message.text) > ALLOWED_CATEGORY_LENGHT:
        await message.answer(f'Длина категории не может превышать {ALLOWED_CATEGORY_LENGHT} символов.',
                             reply_markup=await main_kb.GoBackInlineKeyboard().release_keyboard())
        return
    stmt = insert(Category).values(name=category_name, user_id=message.from_user.id)
    with Session(engine) as session:  # TODO create a async context manager for adding users
        session.execute(stmt)
        session.commit()
    await message.answer(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                         spend_kb.CategoryInlineKeyboardWithAddAndRemove(message.from_user).release_keyboard())
    await state.clear()


@spending_router.callback_query(F.data.startswith('category_'))
async def add_transaction(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TransactionGroup.category_id)
    await state.update_data(category_id=callback.data.split('_')[1])
    await state.set_state(TransactionGroup.amount)
    await callback.answer()
    await callback.message.answer('Введите сумму транзакции.',
                                  reply_markup=await spend_kb.NumberInlineKeyboard().release_keyboard())


@spending_router.callback_query(F.data.startswith('amount_category_'))  # TODO isnt implemented
async def get_transaction_amount(callback: CallbackQuery, state: FSMContext) -> None:
    from random import randint
    amount = callback.data.split('_')[2]  # noqa
    data = await state.get_data()  # noqa
    await callback.answer()
    await callback.message.edit_text(f'Введите сумму транзакции.\nПромежуточный итог: {randint(1, 500)}',
                                     reply_markup=await spend_kb.NumberInlineKeyboard().release_keyboard())


@spending_router.message(TransactionGroup.amount)
async def save_transaction_amount_from_tg_keyboard(message: Message, state: FSMContext) -> None:
    user_amount = message.text.replace(',', '.')
    if not re.match(r'^\d{1,6}(\.\d{0,2})?$', user_amount):
        await message.answer(f'Неправильный формат транзакции.',
                             reply_markup=await spend_kb.NumberInlineKeyboard().release_keyboard())
        return
    await state.update_data(amount=user_amount)
    data = await state.get_data()
    with Session(engine) as session:
        transaction = Transaction(**data)
        session.add(transaction)
        session.commit()
    await state.clear()
    await message.answer('Транзакция успешно записана.')
    await message.answer(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                         spend_kb.CategoryInlineKeyboardWithAddAndRemove(message.from_user).release_keyboard())

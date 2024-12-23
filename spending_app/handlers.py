from collections import namedtuple
import re

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import insert
from sqlalchemy.orm import Session
from aiogram.fsm.context import FSMContext

from database.engine import engine
import keyboards as main_kb
from spending_app.buttons_dataclasses import AddCategoryButtonData, AddExpensesButtonData, RemoveCategoryButtonData
from spending_app.consts import ALLOWED_CATEGORY_LENGHT, GREETING_SPEND_APP_MESSAGE
from spending_app.callbacks import ReturnCallback, ShowNextCallback, ShowPrevCallback
from spending_app.keyboards import (CategoryInlineKeyboardWithAddAndRemove, NumberInlineKeyboard,
                                    RemoveCategoryInlineKeyboard)
from spending_app.models import Category, Transaction
from spending_app.state_groups import CategoryGroup, TransactionGroup


spending_router = Router()


@spending_router.message(F.text == AddExpensesButtonData.text)
@spending_router.callback_query(ReturnCallback.filter(F.direction == "cat"))
@spending_router.callback_query(ShowNextCallback.filter(F.direction == "cat"))
@spending_router.callback_query(ShowPrevCallback.filter(F.direction == "cat"))
async def choose_category(request: Message | CallbackQuery) -> None:
    user_request = getattr(request, 'text', None) or request.data
    method = isinstance(request, Message) and request.answer or await request.answer() and request.message.edit_text
    await method(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                 CategoryInlineKeyboardWithAddAndRemove(request.from_user, user_request).release_keyboard())


@spending_router.callback_query(F.data == RemoveCategoryButtonData.callback_data)
@spending_router.callback_query(ShowNextCallback.filter(F.direction == "rem_cat"))
@spending_router.callback_query(ShowPrevCallback.filter(F.direction == "rem_cat"))
async def select_category_for_removal(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message. \
        edit_text('Выберите категорию для удаления.',
                  reply_markup=await RemoveCategoryInlineKeyboard(callback.from_user,
                                                                  callback.data).release_keyboard())


@spending_router.callback_query(F.data.startswith('remove_category_'))
async def remove_category(callback: CallbackQuery) -> None:
    with Session(engine) as session:
        obj = session.query(Category).filter(Category.id == callback.data.split('_')[2],
                                             Category.user_id == callback.from_user.id).first()
        session.delete(obj)
        session.commit()
    await callback.answer('Категория удалена.')
    await callback.message.edit_text(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                                     CategoryInlineKeyboardWithAddAndRemove(callback.from_user,
                                                                            callback.data).release_keyboard())


@spending_router.callback_query(F.data == AddCategoryButtonData.callback_data)
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
                         CategoryInlineKeyboardWithAddAndRemove(message.from_user, message.text).release_keyboard())
    await state.clear()


@spending_router.callback_query(F.data.startswith('category_'))
async def add_transaction(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TransactionGroup.category_id)
    await state.update_data(category_id=callback.data.split('_')[1])
    await state.set_state(TransactionGroup.amount)
    await callback.answer()
    await callback.message.edit_text('Введите сумму транзакции.',
                                  reply_markup=await NumberInlineKeyboard().release_keyboard())


@spending_router.callback_query(F.data.startswith('amount_category_'))
async def get_transaction_amount(callback: CallbackQuery, state: FSMContext) -> None:
    async def handle_ok_input(amount: str, data: dict, state: FSMContext, callback: CallbackQuery) -> namedtuple:
        if not amount:
            return Response(alert='Значение не может быть пустым.')
        if not data.get('category_id'):
            await state.clear()
            return Response(message='Cообщение устарело и помещено в архив.\nВвод невозможен.')
        if not re.match(r'^\d{1,6}(\.\d{0,2})?$', amount):
            return Response(alert='Неправильный формат транзакции.')

        with Session(engine) as session:
            transaction = Transaction(**data)
            session.add(transaction)
            session.commit()

        await state.clear()
        return Response(alert='Транзакция успешно записана.', message=GREETING_SPEND_APP_MESSAGE, \
            keyboard=CategoryInlineKeyboardWithAddAndRemove(callback.from_user, callback.data))

    Response = namedtuple('PreparedResponse', ('alert', 'message', 'keyboard'),
        defaults=('', 'Введите значение транзакции.\nПроможуточный итог: {}', NumberInlineKeyboard())
    )
    data = await state.get_data()
    current_amount = data.get('amount', '')
    user_input = callback.data.split('_')[2]

    if user_input == 'OK':
        response_obj = await handle_ok_input(current_amount, data, state, callback)
    elif user_input == 'clear':
        await state.update_data(amount='')
        current_amount = ''
        response_obj = Response(alert='Ваш ввод был сброшен.')
    else:
        current_amount += user_input
        await state.update_data(amount=current_amount)
        response_obj = Response()

    await callback.answer(response_obj.alert)
    await callback.message.edit_text(response_obj.message.format(current_amount), reply_markup=await
                                     response_obj.keyboard.release_keyboard())


@spending_router.message(TransactionGroup.amount)
async def save_transaction_amount_from_tg_keyboard(message: Message, state: FSMContext) -> None:
    user_amount = message.text.replace(',', '.')
    if not re.match(r'^\d{1,6}(\.\d{0,2})?$', user_amount):
        await message.answer('Неправильный формат транзакции.',
                             reply_markup=await NumberInlineKeyboard().release_keyboard())
        return
    await state.update_data(amount=user_amount)
    data = await state.get_data()
    with Session(engine) as session:
        transaction = Transaction(**data)
        session.add(transaction)
        session.commit()
    await state.clear()
    await message.answer(GREETING_SPEND_APP_MESSAGE, reply_markup=await
                         CategoryInlineKeyboardWithAddAndRemove(message.from_user, message.text).release_keyboard())

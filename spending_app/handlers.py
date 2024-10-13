from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import delete, insert
from sqlalchemy.orm import Session
from aiogram.fsm.context import FSMContext

import buttons as bt
from database.engine import engine
from settings import MAX_CATEGORY_PER_USER
from spending_app.filters import ReturnCallback, ChooseCategoryMessageFilter
import spending_app.keyboards as kb
from spending_app.models import Category
from spending_app.state_groups import CategoryGroup, TransactionGroup
from users_app.models import User


spending_router = Router()


@spending_router.message(CommandStart())
async def start_conversation(message: Message) -> None:
    user_id = message.from_user.id
    with Session(engine) as session:  # TODO create a async context manager for adding users
        if not session.query(User).filter(User.telegram_id == user_id).count():
            user = User(telegram_id=user_id)
            session.add(user)
            session.commit()
    await message.answer('Привет, это твой Finance buddy', reply_markup=kb.start_keyboard)


@spending_router.callback_query(ReturnCallback.filter(F.direction == "cat"))
@spending_router.message(ChooseCategoryMessageFilter())
async def choose_category(request: Message | CallbackQuery) -> None:
    method = isinstance(request, Message) and request.answer or (await request.answer() and request.message.edit_text)
    await method(f'Выберите, создайте или удалите категорию.\nМаксимум {MAX_CATEGORY_PER_USER} категорий',
                 reply_markup=await kb.CategoryInlineKeyboardWithAddAndRemove(request.from_user).release_keyboard())


@spending_router.callback_query(F.data == bt.REMOVE_CATEGORY_BUTTON_DICT.get('callback_data'))
async def select_category_for_removal(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text('Выберите категорию для удаления.',
                                     reply_markup=await kb.RemoveCategoryInlineKeyboard(callback.from_user) \
                                        .release_keyboard())


@spending_router.callback_query(F.data.startswith('remove_category_'))
async def remove_category(callback: CallbackQuery) -> None:
    stmt = delete(Category).where(Category.id == callback.data.split('_')[2],
                                  Category.user_id == callback.from_user.id)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()
    await callback.answer('Категория удалена.')
    await callback.message.edit_text(
        f'Выберите, создайте или удалите категорию.\nМаксимум {MAX_CATEGORY_PER_USER} категорий',
        reply_markup=await kb.CategoryInlineKeyboardWithAddAndRemove(callback.from_user).release_keyboard()
    )


@spending_router.callback_query(F.data == bt.ADD_CATEGORY_BUTTON_DICT.get('callback_data'))
async def add_category(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CategoryGroup.category_name)
    await callback.answer()
    await callback.message.edit_text('Введите имя категории.',
                                     reply_markup=await kb.GoBackInlineKeyboard().release_keyboard())


@spending_router.message(CategoryGroup.category_name)
async def get_category_name(message: Message, state: FSMContext) -> None:
    category_name = message.text
    stmt = insert(Category).values(name=category_name, user_id=message.from_user.id)
    with Session(engine) as session:  # TODO create a async context manager for adding users
        session.execute(stmt)
        session.commit()
    await message.answer(
        f'Выберите, создайте или удалите категорию.\nМаксимум {MAX_CATEGORY_PER_USER} категорий',
        reply_markup=await kb.CategoryInlineKeyboardWithAddAndRemove(message.from_user).release_keyboard()
    )
    await state.clear()


@spending_router.callback_query(F.data.startswith('category_'))
async def add_transaction(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TransactionGroup.category_name)
    await state.update_data(category_name=callback.data.split('_')[1])
    await state.set_state(TransactionGroup.amount)
    await callback.answer()
    await callback.message.answer('Введите сумму транзакции.',
                                     reply_markup=await kb.NumberInlineKeyboard().release_keyboard())


@spending_router.callback_query(F.data.startswith('amount_category_'))
async def get_transaction_amount(callback: CallbackQuery, state: FSMContext) -> None:
    from random import randint
    amount = callback.data.split('_')[2]
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(f'Введите сумму транзакции.\nПромежуточный итог: {randint(1, 500)}',
                                     reply_markup=await kb.NumberInlineKeyboard().release_keyboard())

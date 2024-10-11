from aiogram.fsm.state import State, StatesGroup


class CategoryGroup(StatesGroup):
    category_name = State()


class TransactionGroup(CategoryGroup):
    amount = State()

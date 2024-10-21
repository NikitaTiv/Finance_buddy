from aiogram.fsm.state import State, StatesGroup


class CategoryGroup(StatesGroup):
    category_name: State = State()


class TransactionGroup(StatesGroup):
    category_id: State = State()
    amount: State = State()

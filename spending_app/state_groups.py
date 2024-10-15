from decimal import Decimal
from aiogram.fsm.state import State, StatesGroup


class CategoryGroup(StatesGroup):
    category_name: str = State()


class TransactionGroup(StatesGroup):
    category_id: int = State()
    amount: Decimal = State()

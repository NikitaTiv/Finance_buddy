from dataclasses import dataclass

from buttons_base import ClearCacheMixin, GetAttrMixin


@dataclass
class AddExpensesButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = '🫰 Управление расходами'


@dataclass
class BackButtonButtonData(GetAttrMixin):
    text: str = '⬅️ Вернуться назад'
    callback_data: str = 'cat'


@dataclass
class AddCategoryButtonData(GetAttrMixin):
    text: str = '➕ Добавить'
    callback_data: str = 'add_category'


@dataclass
class RemoveCategoryButtonData(GetAttrMixin):
    text: str = '❌ Удалить'
    callback_data: str = 'remove_category'

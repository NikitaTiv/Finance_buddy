from abc import ABC, abstractmethod
from dataclasses import dataclass

from buttons_base import ClearCacheMixin, GetAttrMixin


@dataclass
class AddExpensesButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = '🫰 Управление расходами'


@dataclass
class LimitsButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = '🚧 Лимиты'


@dataclass
class BaseBackDataClass(GetAttrMixin, ABC):
    text: str = '⬅️ Вернуться назад'

    @property
    @abstractmethod
    def callback_data(self) -> str:
        pass


@dataclass
class BackToCatsButtonData(BaseBackDataClass):
    callback_data: str = 'cat'


@dataclass
class BackToLimitsButtonData(BaseBackDataClass):
    callback_data: str = 'limit'


@dataclass
class AddCategoryButtonData(GetAttrMixin):
    text: str = '➕ Добавить'
    callback_data: str = 'add_category'


@dataclass
class RemoveCategoryButtonData(GetAttrMixin):
    text: str = '❌ Удалить'
    callback_data: str = 'rem_cat'


@dataclass
class ShowNextCategoriesButtonData(GetAttrMixin):
    text: str = 'Показать еще 🔽'


@dataclass
class ShowPrevCategoriesButtonData(GetAttrMixin):
    text: str = 'Предыдущие категории 🔼'

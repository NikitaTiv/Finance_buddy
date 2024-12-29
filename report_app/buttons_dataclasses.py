from dataclasses import dataclass

from buttons_base import ClearCacheMixin, GetAttrMixin


@dataclass
class GetReportButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = '🧮 Получить отчет'


@dataclass
class GetReportPerMonthButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = 'Oтчет за '


@dataclass
class BackToReportButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = '⬅️ Вернуться назад'

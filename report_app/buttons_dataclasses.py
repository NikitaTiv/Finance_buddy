from dataclasses import dataclass

from buttons_base import ClearCacheMixin, GetAttrMixin


@dataclass
class GetReportButtonData(ClearCacheMixin, GetAttrMixin):
    text: str = '🧮 Получить отчет'

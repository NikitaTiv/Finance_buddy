from sqlalchemy.orm.query import Query

from typing import Generator, Iterable, Optional

import buttons_base as bt
from errors import IncorrectlyСonfiguredException
from report_app.buttons_dataclasses import GetReportButtonData
from settings import MAX_CATEGORY_PER_USER
from spending_app.buttons_dataclasses import (AddCategoryButtonData, AddExpensesButtonData, BackButtonData,
                                              RemoveCategoryButtonData)
from spending_app.callbacks import ReturnCallback


class GoBackHeaderMixin:
    def prepare_headers(self, db_query: Optional[Query]) -> Iterable[bt.InlineButton]:
        yield bt.InlineButton(text=BackButtonData.text, callback_data=ReturnCallback(
            direction=BackButtonData.callback_data).pack())


class AddRemoveButtonMixin:
    def prepare_headers(self, db_query: Optional[Query]) -> Generator[bt.InlineButton, None, None]:
        qty_method = getattr(self, 'get_results_qty', None)
        if not qty_method:
            raise IncorrectlyСonfiguredException(f'{self.__class__.__name__} is incorrectly configured')
        category_qty = qty_method(db_query)
        yield bt.InlineButton(is_applicable = category_qty < MAX_CATEGORY_PER_USER,
                              **AddCategoryButtonData.get_attrs())
        yield bt.InlineButton(is_applicable = bool(category_qty), **RemoveCategoryButtonData.get_attrs())


class NumbersMixin:
    @property
    def number_per_row(self) -> tuple[int]:
        return (3,)

    def prepare_content(self, db_query: Optional[Query]) -> Iterable[bt.InlineButton]:
        return (bt.InlineButton(text=str(number), callback_data=f'amount_category_{number}')
                    for number in range(1, 10))

    def prepare_footer(self, db_query: Optional[Query]) -> Generator[bt.InlineButton, None, None]:
        yield bt.InlineButton(text='⬅️', callback_data=ReturnCallback(
            direction=BackButtonData.callback_data).pack())
        yield bt.InlineButton(text=str(0), callback_data='amount_category_0')
        yield bt.InlineButton(text='OK', callback_data='amount_category_OK')


class MainKeyboardMixin:
    def prepare_content(self, db_query: Optional[Query]) -> Generator[bt.ReplyButton, None, None]:
        yield bt.ReplyButton(**AddExpensesButtonData.get_attrs())
        yield bt.ReplyButton(**GetReportButtonData.get_attrs())

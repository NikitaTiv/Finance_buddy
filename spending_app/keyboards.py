from typing import Generator, Iterable
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm.query import Query
from sqlalchemy import func

import buttons_base as bt
from database.engine import engine
from keyboards import BaseInlineKeyboard
from settings import MAX_CATEGORY_PER_USER, MAX_CATEGORY_PER_PAGE
from keyboard_mixins import AddRemoveButtonMixin, GoBackHeaderMixin, NumbersMixin
from spending_app.buttons_dataclasses import RemoveCategoryButtonData, ShowNextCategoriesButtonData, ShowPrevCategoriesButtonData
from spending_app.callbacks import ShowNextCallback, ShowPrevCallback
from spending_app.models import Category, Transaction
from users_app.models import User


class CategoryInlineKeyboard(BaseInlineKeyboard):
    def __init__(self, user, user_request):
        super().__init__()
        self.user: User = user
        self.user_request: str = user_request

    @property
    def is_show_next_request(self):
        return self.user_request.split(':')[0] == 'show_next'

    def limit_db_query(self, db_query: Query) -> Query:
        if self.is_show_next_request:
            return db_query.offset(MAX_CATEGORY_PER_PAGE)
        return db_query.limit(MAX_CATEGORY_PER_PAGE)

    async def make_db_query(self) -> Query:
        TransactionAlias = aliased(Transaction)
        with Session(engine) as session:
            return session.query(Category).outerjoin(TransactionAlias).filter(Category.user_id == self.user.id) \
                .group_by(Category.id).order_by(func.sum(TransactionAlias.amount).desc())

    def prepare_content(self, db_query: Query) -> Iterable[bt.InlineButton]:
        return (bt.InlineButton(text=row.name, callback_data=f'category_{row.id}')
                for row in self.limit_db_query(db_query))

    def prepare_footer(self, results: Query) -> Generator[bt.InlineButton, None, None]:
        if self.is_show_next_request:
            button_text = ShowPrevCategoriesButtonData
            button_callback_data = ShowPrevCallback
        else:
            button_text = ShowNextCategoriesButtonData
            button_callback_data = ShowNextCallback

        direction = rem_data if (rem_data := RemoveCategoryButtonData.callback_data) in self.user_request else 'cat'

        yield bt.InlineButton(is_applicable=self.get_results_qty(results) > MAX_CATEGORY_PER_PAGE,
                              text=button_text.text,
                              callback_data=button_callback_data(direction=direction).pack())


class RemoveCategoryInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    def prepare_content(self, db_query: Query) -> Iterable[bt.InlineButton]:
        return (bt.InlineButton(text=row.name, callback_data=f'remove_category_{row.id}')
                for row in self.limit_db_query(db_query))


class CategoryInlineKeyboardWithAddAndRemove(AddRemoveButtonMixin, CategoryInlineKeyboard):
    @property
    def number_per_row(self) -> tuple[int]:
        category_qty = self.get_results_qty(self.db_query)
        if 0 < category_qty < MAX_CATEGORY_PER_USER:
            return (2, 1)
        return (1,)


class CategoryGoBackInlineKeyboard(GoBackHeaderMixin, CategoryInlineKeyboard):
    pass


class NumberInlineKeyboard(NumbersMixin, BaseInlineKeyboard):
    pass

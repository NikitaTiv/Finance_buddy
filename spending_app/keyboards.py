from typing import Generator, Iterable, Optional
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm.query import Query
from sqlalchemy import func

import buttons_base as bt
from database.engine import engine
from keyboards import BaseInlineKeyboard
from settings import MAX_CATEGORY_PER_USER, MAX_CATEGORY_PER_PAGE
from keyboard_mixins import (AddRemoveButtonMixin, GoBackToCatsHeaderMixin, GoBackToLimitsHeaderMixin,
                             GoBackToTransactionsHeaderMixin, NumbersMixin)
from spending_app.buttons_dataclasses import (BackToLimitsButtonData, LimitsButtonData, RemoveCategoryButtonData,
                                              ShowNextCategoriesButtonData, ShowPrevCategoriesButtonData)
from spending_app.callbacks import (EditLimitCallback, LimitCallback, RemoveLimitCallback, RemoveTransactionCallback,
                                    ShowNextCallback, ShowPrevCallback)
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

    @staticmethod
    def try_to_convert_request(request):
        convert_dict = {
            LimitsButtonData.text: BackToLimitsButtonData.callback_data
        }
        return convert_dict.get(request, request)

    def prepare_footer(self, results: Query) -> Generator[bt.InlineButton, None, None]:
        directions = (
            RemoveCategoryButtonData.callback_data,
            BackToLimitsButtonData.callback_data,
        )
        direction = next((dir for dir in directions if dir in self.try_to_convert_request(self.user_request)), 'cat')

        if self.is_show_next_request:
            button_text = ShowPrevCategoriesButtonData
            button_callback_data = ShowPrevCallback
        else:
            button_text = ShowNextCategoriesButtonData
            button_callback_data = ShowNextCallback

        yield bt.InlineButton(is_applicable=self.get_results_qty(results) > MAX_CATEGORY_PER_PAGE,
                              text=button_text.text,
                              callback_data=button_callback_data(direction=direction).pack())


class RemoveCategoryInlineKeyboard(GoBackToCatsHeaderMixin, CategoryInlineKeyboard):
    def prepare_content(self, db_query: Query) -> Iterable[bt.InlineButton]:
        return (bt.InlineButton(text=row.name, callback_data=f'remove_category_{row.id}')
                for row in self.limit_db_query(db_query))


class CategoryInlineKeyboardWithAddAndRemove(AddRemoveButtonMixin, CategoryInlineKeyboard):
    @property
    def number_per_row(self) -> tuple[int]:
        category_qty = self.get_results_qty(self.db_query)
        if 0 < category_qty < MAX_CATEGORY_PER_USER:
            return (1, 2, 1)
        return (1,)


class CategoryGoBackInlineKeyboard(GoBackToCatsHeaderMixin, CategoryInlineKeyboard):
    pass


class NumberInlineKeyboard(NumbersMixin, GoBackToCatsHeaderMixin, BaseInlineKeyboard):
    @property
    def number_per_row(self) -> tuple[int]:
        return (1, 3)


class LimitCategoryInlineKeyboard(CategoryInlineKeyboard):
    def prepare_content(self, db_query: Query) -> Iterable[bt.InlineButton]:
        return (bt.InlineButton(text=f'{row.name} - {row.limit or "❌"}', callback_data=LimitCallback(
            direction=str(row.id)).pack()) for row in self.limit_db_query(db_query))


class ViewLimitInlineKeyboard(GoBackToLimitsHeaderMixin, BaseInlineKeyboard):
    def __init__(self, category_id) -> None:
        super().__init__()
        self.category_id = category_id

    def prepare_content(self, db_query: Optional[Query]) -> Generator[bt.InlineButton, None, None]:
        yield bt.InlineButton(text='Редактировать лимит 📝', callback_data=EditLimitCallback(
            direction=str(self.category_id)).pack())
        yield bt.InlineButton(text='Удалить лимит 🗑', callback_data=RemoveLimitCallback(
            direction=str(self.category_id)).pack())


class TransactionInlineKeyboard(GoBackToTransactionsHeaderMixin, BaseInlineKeyboard):
    def __init__(self, user_id: str) -> None:
        super().__init__()
        self.user_id = user_id

    async def make_db_query(self) -> Query:
        with Session(engine) as session:
            return session.query(Transaction.id, Transaction.amount, Category.name) \
                .join(Category) \
                .filter(Category.user_id == self.user_id) \
                .order_by(Transaction.id.desc()) \
                .limit(10)

    def prepare_content(self, db_query: Query) -> Iterable[bt.InlineButton]:
        return (bt.InlineButton(text=f'{row[2]} - {row[1]}', callback_data=RemoveTransactionCallback(
            direction=str(row[0])).pack()) for row in db_query.all())


class RemoveTransactionInlineKeyboard(BaseInlineKeyboard):
    def __init__(self, transaction_id: str) -> None:
        super().__init__()
        self.transaction_id = transaction_id

    @property
    def number_per_row(self) -> tuple[int]:
        return (2,)

    def prepare_content(self, db_query: Query) -> Generator[bt.InlineButton, None, None]:
        yield bt.InlineButton(text='✅ Да', callback_data=RemoveTransactionCallback(
            direction=f'{self.transaction_id}_yes').pack())
        yield bt.InlineButton(text='⛔️ Нет', callback_data=RemoveTransactionCallback(
            direction=f'{self.transaction_id}_no').pack())

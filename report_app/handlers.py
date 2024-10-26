import io
from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

import buttons as bt
from database.engine import engine
from report_app.utils import generate_file_for_report, get_total_sum
from spending_app.models import Category, Transaction

report_router = Router()


@report_router.message(F.text == bt.GET_REPORT_BUTTON_DICT['text'])
async def get_report(message: Message) -> None:
    transaction_alias = aliased(Transaction)
    category_alias = aliased(Category)

    with Session(engine) as session:
        category_data = session.query(
            category_alias.name.label('category'), func.sum(transaction_alias.amount).label('total_amount')
        ).filter(category_alias.user_id.is_(getattr(message.from_user, 'id'))) \
            .join(category_alias, transaction_alias.category).group_by(category_alias.name). \
            order_by(func.sum(transaction_alias.amount).desc()).all()

    file = generate_file_for_report(category_data, get_total_sum(category_data))

    await message.answer_photo(file)


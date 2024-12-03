from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from database.engine import engine
from report_app.buttons_dataclasses import GetReportButtonData
from report_app.utils import ReportFileGenerator
from spending_app.models import Category, Transaction

report_router = Router()


@report_router.message(F.text == GetReportButtonData.text)
async def get_report(message: Message) -> None:
    transaction_alias = aliased(Transaction)
    category_alias = aliased(Category)

    with Session(engine) as session:
        category_data = session.query(
            category_alias.name.label('category'), func.sum(transaction_alias.amount).label('total_amount')
        ).filter(category_alias.user_id.is_(getattr(message.from_user, 'id'))) \
            .join(category_alias, transaction_alias.category).group_by(category_alias.name). \
            order_by(func.sum(transaction_alias.amount).desc()).all()

    file = ReportFileGenerator.generate_file_for_report(category_data)

    await message.answer_photo(file)

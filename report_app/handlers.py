from datetime import datetime
import locale

from aiogram import F, Router
from aiogram.types import Message
from dateutil.relativedelta import relativedelta
import pymorphy3
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from database.engine import engine
import keyboards as kb
from report_app.buttons_dataclasses import GetReportButtonData, GetReportPerMonthButtonData
from report_app.utils import ReportFileGenerator, get_month_number
from spending_app.models import Category, Transaction

report_router = Router()


@report_router.message(F.text == GetReportButtonData.text)
async def get_report(message: Message) -> None:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    morph = pymorphy3.MorphAnalyzer()
    current_date = datetime.now()
    previous_months = (
        morph.parse((current_date - relativedelta(months=i)).strftime('%B'))[0].normal_form.capitalize() +
        ' ' + (current_date - relativedelta(months=i)).strftime('%Y') for i in range(3)
    )
    await message.answer('За какой месяц вы хотите получить отчет?',
                         reply_markup=await kb.GetReportPerMonthReplyKeyboard(previous_months).release_keyboard())


@report_router.message(F.text.startswith(GetReportPerMonthButtonData.text))
async def get_report_per_month(message: Message) -> None:
    month, year = message.text.split(' ')[2:]
    month_num = get_month_number(month)
    try:
        converted_year = int(year)
        start_date = datetime(converted_year, month_num, 1)
        end_date = datetime(converted_year, month_num + 1, 1) if month_num < 12 \
            else datetime(converted_year + 1, 1, 1)
    except (TypeError, ValueError):
        return await message.answer('Неправильный ввод.')
    transaction_alias = aliased(Transaction)
    category_alias = aliased(Category)

    with Session(engine) as session:
        category_data = session.query(
            category_alias.name.label('category'),
            category_alias.limit.label('limit'),
            func.sum(transaction_alias.amount).label('total_amount')
        ).filter(
            category_alias.user_id.is_(getattr(message.from_user, 'id')),
            transaction_alias.created_at >= start_date,
            transaction_alias.created_at < end_date
        ).join(transaction_alias, category_alias.id == transaction_alias.category_id) \
            .group_by(category_alias.name) \
            .order_by(func.sum(transaction_alias.amount).desc()) \
            .all()

    file = ReportFileGenerator(data=category_data).generate_file_for_report()

    await message.answer_photo(file)

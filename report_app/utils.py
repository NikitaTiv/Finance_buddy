import io
from decimal import Decimal

from aiogram import types
from PIL import Image, ImageDraw, ImageFont
import sqlalchemy

from report_app.consts import (INDENTS_BETWEEN_LINES_IN_REPORT as indent_line,
                               INDENTS_FROM_LEFT_SIDE_IN_REPORT as indent_left_side,
                               ADDITIONAL_SPACE_IN_REPORT as additional_space,
                               REPORT_WIDTH)


def get_total_sum(category_data: list[sqlalchemy.engine.row.Row]) -> Decimal:
    return sum([result[1] for result in category_data])

def prepare_content(data: list[sqlalchemy.engine.row.Row], total_amount: Decimal) -> str:
    return ['Ваши расходы:'] + [f'{category:.<20}{amount}' for category, amount in data] + [f'Итого: {total_amount}']


def generate_file_for_report(
        category_data: list[sqlalchemy.engine.row.Row], total_amount: Decimal
    ) -> types.BufferedInputFile:
    text_list = prepare_content(category_data, total_amount)
    img = Image.new('RGB', (REPORT_WIDTH, len(text_list)*indent_line+additional_space), 'white')
    draw = ImageDraw.Draw(img)
    header_font = ImageFont.truetype("fonts/DroidSansBold.ttf")
    content_font = ImageFont.truetype("fonts/DroidSansMono.ttf")
    draw.text((indent_left_side, indent_line), text_list.pop(0), fill='black', font=header_font)
    for index, text in enumerate(text_list, start=2):
        draw.text((indent_left_side, index*indent_line), text, fill='black', font=content_font)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='png')
    img_bytes.seek(0)
    return types.BufferedInputFile(img_bytes.read(), filename="buffer img.jpg")

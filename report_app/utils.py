import calendar
from datetime import date
import io
from decimal import Decimal
from typing import Optional

from aiogram import types
from PIL import Image, ImageDraw, ImageFont
import sqlalchemy


class ReportFileGenerator:
    indent_between_lines = 20
    indent_from_left_side = 30
    additional_space = 40

    def __init__(self, data: list[sqlalchemy.engine.row.Row]) -> None:
        self.category_data = data

    def get_total_amount(self) -> Decimal:
        return sum((result[2] for result in self.category_data))  # TODO move this to DB query

    @property
    def report_widht(self) -> int:
        if any(filter(lambda x: x[1], self.category_data)):
            return 280
        return 230

    @staticmethod
    def prepare_limit_data(limit: Optional[int]) -> str:
        if not limit:
            return ''
        today = date.today()
        total_days_in_month = calendar.monthrange(today.year, today.month)[1]
        return f'/{int(today.day * limit / total_days_in_month)}/{limit}'

    def prepare_report_content(self, total_amount: Decimal) -> list[str]:
        return [
            'Ваши расходы:',
            *(f'{category:.<20}{amount}{self.prepare_limit_data(limit)}'
                  for category, limit, amount in self.category_data),
            f'Итого: {total_amount}'
        ]

    def draw_image(self, list_with_calculations: list[str]) -> Image:
        img = Image.new('RGB', (
            self.report_widht,
            len(list_with_calculations)*self.indent_between_lines+self.additional_space
        ), 'white')
        draw = ImageDraw.Draw(img)
        header_font = ImageFont.truetype("fonts/DroidSansBold.ttf")
        content_font = ImageFont.truetype("fonts/DroidSansMono.ttf")
        draw.text((self.indent_from_left_side, self.indent_between_lines),
                  list_with_calculations.pop(0), fill='black', font=header_font)
        for index, text in enumerate(list_with_calculations, start=2):
            draw.text((self.indent_from_left_side, index*self.indent_between_lines),
                      text, fill='black', font=content_font)
        return img

    def generate_file_for_report(self) -> types.BufferedInputFile:
        total_amount = self.get_total_amount()
        text_list = self.prepare_report_content(total_amount)
        img = self.draw_image(text_list)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='png')
        img_bytes.seek(0)
        return types.BufferedInputFile(img_bytes.read(), filename="buffer img.jpg")

import io
from decimal import Decimal

from aiogram import types
from PIL import Image, ImageDraw, ImageFont
import sqlalchemy


class ReportFileGenerator:
    indent_between_lines = 20
    indent_from_left_side = 30
    report_widht = 230
    additional_space = 40

    @staticmethod
    def get_total_amount(category_data: list[sqlalchemy.engine.row.Row]) -> Decimal:
        return sum([result[1] for result in category_data])  # TODO move this to DB query

    @staticmethod
    def prepare_report_content(data: list[sqlalchemy.engine.row.Row], total_amount: Decimal) -> list[str]:
        return [
            'Ваши расходы:',
            *[f'{category:.<20}{amount}' for category, amount in data],
            f'Итого: {total_amount}'
        ]

    @classmethod
    def draw_image(cls, list_with_calculations: list[str]) -> Image:
        img = Image.new('RGB', (
            cls.report_widht,
            len(list_with_calculations)*cls.indent_between_lines+cls.additional_space
        ), 'white')
        draw = ImageDraw.Draw(img)
        header_font = ImageFont.truetype("fonts/DroidSansBold.ttf")
        content_font = ImageFont.truetype("fonts/DroidSansMono.ttf")
        draw.text((cls.indent_from_left_side, cls.indent_between_lines),
                  list_with_calculations.pop(0), fill='black', font=header_font)
        for index, text in enumerate(list_with_calculations, start=2):
            draw.text((cls.indent_from_left_side, index*cls.indent_between_lines),
                      text, fill='black', font=content_font)
        return img

    @classmethod
    def generate_file_for_report(cls, category_data: list[sqlalchemy.engine.row.Row]) -> types.BufferedInputFile:
        total_amount = cls.get_total_amount(category_data)
        text_list = cls.prepare_report_content(category_data, total_amount)
        img = cls.draw_image(text_list)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='png')
        img_bytes.seek(0)
        return types.BufferedInputFile(img_bytes.read(), filename="buffer img.jpg")

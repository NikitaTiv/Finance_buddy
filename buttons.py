from aiogram.types import InlineKeyboardButton, KeyboardButton


class ApplicableMixin:
    def __init__(self, *args, **kwargs):
        self.is_applicable: bool = kwargs.get('is_applicable', True)


class InlineButton(InlineKeyboardButton, ApplicableMixin):
    """
    Class for creating custom inline buttons with 'is_applicable' attribute.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ApplicableMixin.__init__(self, *args, **kwargs)


class ReplyButton(KeyboardButton, ApplicableMixin):
    """
    Class for creating custom reply buttons with 'is_applicable' attribute.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ApplicableMixin.__init__(self, *args, **kwargs)


# Spending app
ADD_EXPENSES_BUTTON_DICT = {'text': '🫰 Добавить расходы'}
GET_REPORT_BUTTON_DICT = {'text': '🧮 Получить отчет'}
BACK_BUTTON_DICT = {'text': '⬅️ Вернуться назад', 'callback_data': 'cat'}
ADD_CATEGORY_BUTTON_DICT = {'text': '➕ Добавить', 'callback_data': 'add_category'}
REMOVE_CATEGORY_BUTTON_DICT = {'text': '❌ Удалить', 'callback_data': 'remove_category'}

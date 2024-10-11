from aiogram.types import InlineKeyboardButton, KeyboardButton


class ApplicableMixin:
    def __init__(self, *args, **kwargs):
        self.is_applicable: bool = kwargs.get('is_applicable', True)


class InlineButton(InlineKeyboardButton, ApplicableMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ApplicableMixin.__init__(self, *args, **kwargs)


class ReplyButton(KeyboardButton, ApplicableMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ApplicableMixin.__init__(self, *args, **kwargs)


# Spending app
ADD_EXPENSES_BUTTON_DICT = {'text': 'Добавить расходы'}
BACK_BUTTON_DICT = {'text':'⬅️ Вернуться назад', 'callback_data': 'cat'}
ADD_CATEGORY_BUTTON_DICT = {'text': '➕ Добавить категорию', 'callback_data': 'add_category'}
REMOVE_CATEGORY_BUTTON_DICT = {'text': '❌ Удалить категорию', 'callback_data': 'remove_category'}

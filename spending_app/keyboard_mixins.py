from spending_app.filters import ReturnCallback

import buttons as bt


class GoBackHeaderMixin:
    @staticmethod
    def prepare_headers(results):
        return [
            bt.InlineButton(text=bt.BACK_BUTTON_DICT.get('text'),
                            callback_data=ReturnCallback(direction=bt.BACK_BUTTON_DICT.get('callback_data')).pack())
        ]


class AddRemoveButtonMixin:
    @staticmethod
    def prepare_headers(results):
        return [bt.InlineButton(is_applicable=len(results) < 8, **bt.ADD_CATEGORY_BUTTON_DICT),
                bt.InlineButton(is_applicable=bool(results), **bt.REMOVE_CATEGORY_BUTTON_DICT)]

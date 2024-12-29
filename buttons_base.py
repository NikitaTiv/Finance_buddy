from typing import Any, Tuple

from aiogram.types import InlineKeyboardButton, KeyboardButton


class GetAttrMixin:
    @classmethod
    def get_attrs(cls):
        return {attr: getattr(cls, attr)
                for attr in cls.__dict__
                if not attr.startswith('__') and not callable(getattr(cls, attr))}


class ClearCacheMeta(type):
    no_cache_messages: list[str] = []

    def __new__(cls, name: str, bases: Tuple[Any], attrs: dict[str, Any]) -> 'ClearCacheMixin':
        if msg := attrs.get('text'):
            cls.no_cache_messages.append(msg)
        return super().__new__(cls, name, bases, attrs)


class ClearCacheMixin(metaclass=ClearCacheMeta):
    """Add to a button dataclass to reset a fsm when a button called."""
    pass


class ApplicableMixin:
    def __init__(self, *args: Any, **kwargs: Any):
        self.is_applicable: bool = kwargs.get('is_applicable', True)


class InlineButton(InlineKeyboardButton, ApplicableMixin):
    """
    Class for creating custom inline buttons with 'is_applicable' attribute.
    """
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        ApplicableMixin.__init__(self, *args, **kwargs)


class ReplyButton(KeyboardButton, ApplicableMixin):
    """
    Class for creating custom reply buttons with 'is_applicable' attribute.
    """
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        ApplicableMixin.__init__(self, *args, **kwargs)

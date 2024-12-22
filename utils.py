from glob import glob
import inspect
import re
import sys
from typing import Optional

from buttons_base import ClearCacheMixin


class MessageCacheChecker:
    """
    Prevents reply buttons from being blocked due to cache.
    Gets all objects that inherit from the ClearCacheMixin class and
    checks that the user's message is the text of such an inheritor.

    :param message: Message from user.
    :return: Should the cache be cleared.
    :rtype: bool
    """
    def __init__(self, message: Optional[str], callback: Optional[str]) -> None:
        self.message = message
        self.callback = callback

    @staticmethod
    def convert_paths(py_button_modules: list[str]) -> map:
        return map(lambda py_path: re.sub(r'[/\\]', '.', py_path[:-3]), py_button_modules)

    @classmethod
    def get_eligible_modules(cls) -> map:
        button_modules = glob('**/buttons_dataclasses.py', recursive=True)
        return cls.convert_paths(button_modules)

    def is_valid_class(self, obj) -> bool:
        return hasattr(obj, 'text') and issubclass(obj, ClearCacheMixin)

    def filter_classes(self, classes: list[object]) -> filter:
        return filter(self.is_valid_class, classes)

    def get_classes(self, py_modules: map) -> filter:
        classes = []
        for module in py_modules:
            classes.extend(map(lambda x: x[1], inspect.getmembers(sys.modules[module], inspect.isclass)))
        return self.filter_classes(classes)

    def state_should_be_cleared(self) -> bool:
        if self.callback and self.callback.startswith('amount_category'):
            return False

        if not self.message:
            return True

        button_modules = self.get_eligible_modules()

        button_classes = self.get_classes(button_modules)

        return any(self.message == button_cls.text for button_cls in button_classes)

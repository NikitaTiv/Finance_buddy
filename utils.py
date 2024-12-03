from glob import glob
import inspect
import re
import sys

from buttons_base import ClearCacheMixin


class MessageCacheChecker:  # TODO Use cache
    """
    Prevents reply buttons from being blocked due to cache.
    Gets all objects that inherit from the ClearCacheMixin class and
    checks that the user's message is the text of such an inheritor.

    :param message: Message from user.
    :return: Should the cache be cleared.
    :rtype: bool
    """
    def __init__(self, message: str) -> None:
        self.message = message

    @staticmethod
    def convert_paths(py_button_modules: list[str]) -> map:
        return map(lambda py_path: re.sub(r'[/\\]', '.', py_path[:-3]), py_button_modules)

    @classmethod
    def get_eligible_modules(cls) -> map:
        py_button_modules = glob('**/buttons_dataclasses.py', recursive=True)
        return cls.convert_paths(py_button_modules)

    @staticmethod
    def filter_classes(classes: list[object]):
        return filter(lambda obj: (getattr(obj, 'text', None) and issubclass(obj, ClearCacheMixin)), classes)

    @classmethod
    def get_classes(cls, py_modules: map) -> filter:
        classes = []
        for module in py_modules:
            classes.extend(map(lambda x: x[1], inspect.getmembers(sys.modules[module], inspect.isclass)))
        return cls.filter_classes(classes)

    def state_should_be_cleared(self) -> bool:
        py_modules = self.get_eligible_modules()
        return self.message in map(lambda x: x.text, self.get_classes(py_modules))

from abc import ABCMeta, abstractmethod
from functools import wraps


class Formatter(metaclass=ABCMeta):

    def single(self, func):
        """Decorator to format a single item."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            item = func(*args, **kwargs)
            return self.format_single(item)

        return wrapped

    def multiple(self, func):
        """Decorator to format multiple items."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            items = func(*args, **kwargs)
            return self.format_multiple(items)

        return wrapped

    def single_with_status(self, status):
        """Decorator to format a single item with status."""

        def dectorator(func):

            @wraps(func)
            def wrapped(*args, **kwargs):
                item = func(*args, **kwargs)
                return self.format_single(item), status

            return wrapped

        return dectorator

    def multiple_with_status(self, status):
        """Decorator to format multiple items with status."""

        def dectorator(func):

            @wraps(func)
            def wrapped(*args, **kwargs):
                items = func(*args, **kwargs)
                return self.format_multiple(items), status

            return wrapped

        return dectorator

    @abstractmethod
    def format_single(self, item):
        raise NotImplementedError

    def format_multiple(self, items):
        content = []
        if items:
            for item in items:
                content.append(self.format_single(item))
        return content

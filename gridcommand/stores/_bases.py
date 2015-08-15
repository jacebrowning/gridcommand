from abc import ABCMeta, abstractmethod


class Store(metaclass=ABCMeta):  # pragma: no cover (abstract)

    @abstractmethod
    def create(self, item):
        """Write the item to the store."""
        raise NotImplementedError

    @abstractmethod
    def read(self, key):
        """Read a single item by it's key."""
        raise NotImplementedError

    @abstractmethod
    def filter(self, **kwargs):
        """Read all items matching filter options."""
        raise NotImplementedError

    @abstractmethod
    def update(self, item):
        """"Replace an item in the store."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, item):
        """Remove an item from the store."""
        raise NotImplementedError

from abc import ABCMeta, abstractmethod


class Store(metaclass=ABCMeta):

    @abstractmethod
    def create(self, item):
        raise NotImplementedError

    @abstractmethod
    def read(self, item):
        raise NotImplementedError

    @abstractmethod
    def update(self, item):
        raise NotImplementedError

    @abstractmethod
    def delete(self, item):
        raise NotImplementedError

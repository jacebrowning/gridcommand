from abc import ABCMeta


class Exceptions:

    duplicate = ValueError
    missing = KeyError


class Service(metaclass=ABCMeta):

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()

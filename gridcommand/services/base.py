from abc import ABCMeta


class Exceptions:

    duplicate = ValueError
    missing = KeyError
    invalid = ValueError


class Service(metaclass=ABCMeta):

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()

from abc import ABCMeta


class Exceptions:

    duplicate_value = ValueError
    not_found = KeyError
    invalid_input = ValueError
    permission_denied = ValueError
    missing_input = ValueError
    authentication_failed = ValueError


class Service(metaclass=ABCMeta):

    def __init__(self, exceptions=None):
        self.exceptions = exceptions or Exceptions()

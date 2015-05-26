"""Classes representing turns in a game."""

from .move import Moves


class Turn:

    """An individual turn for a player."""

    def __init__(self):
        super().__init__()
        self.moves = Moves()
        self.done = False

    def __repr__(self):
        return "<turn>"


class Turns(list):

    """A list of turns in a game for each player."""

    def __repr__(self):
        return "<{} turn{}>".format(len(self), "" if len(self) == 1 else "s")

    @property
    def current(self):
        """Get the most recent turn."""
        try:
            return self[-1]
        except IndexError:
            return None

    def find(self, number, exc=ValueError):
        try:
            return self[number - 1]
        except IndexError:
            raise exc("The turn '{}' does not exist.".format(number))

"""Classes representing turns in a game."""

from .move import Moves


class Turn:

    """An individual turn for a player."""

    def __init__(self, done=False):
        self.moves = Moves()
        self.done = done

    def __repr__(self):
        return "<turn: {}done>".format("" if self.done else "not ")

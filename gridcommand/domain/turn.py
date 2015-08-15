"""Classes representing turns in a game."""

from .move import Moves


class Turn:

    """An individual turn for a player."""

    def __init__(self, done=False):
        self.moves = Moves()
        self.done = done

    def __repr__(self):
        return "<turn: {}>".format("finished" if self.done else "started")

    def finish(self, exc=ValueError):
        """Mark the current turn as complete."""
        if self.done:
            raise exc("The turn has already finished.")
        self.done = True

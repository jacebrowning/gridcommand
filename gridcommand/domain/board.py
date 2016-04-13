"""Classes representing boards."""

import copy

from .. import common


log = common.logger(__name__)


class Board:
    """The board for a game."""

    @classmethod
    def randomize(cls, players):
        """Create a new random board for the players."""
        # TODO: implement randomize
        print(players)
        return cls()

    def update(self, players):
        """Update the board state from the player's moves."""
        # TODO: implement update
        print(players)
        return copy.copy(self)

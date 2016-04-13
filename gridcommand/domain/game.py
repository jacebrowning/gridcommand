"""Classes representing games."""

import time
import string
import random

from .. import common
from .player import Players
from .board import Board

log = common.logger(__name__)


class Game:
    """An individual game instance."""

    KEY_CHARS = string.ascii_lowercase + string.digits
    KEY_LENGTH = 8

    def __init__(self, key=None, timestamp=None):
        self.key = key or self._generate_key()
        self.timestamp = timestamp or self._get_timestamp()
        self.players = Players()
        self.turn = 0
        self.board = None

    def __repr__(self):
        return "<game: {}>".format(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def _generate_key():
        return ''.join(random.choice(Game.KEY_CHARS)
                       for _ in range(Game.KEY_LENGTH))

    @staticmethod
    def _get_timestamp():
        return int(time.time())

    def create_player(self, code, exc=ValueError):
        if self.started:
            raise exc("Game has already started.")
        return self.players.create(code, exc=exc)

    def delete_player(self, color, exc=ValueError):
        if self.started:
            raise exc("Game has already started.")
        self.players.delete(color)

    @property
    def started(self):
        return self.turn > 0

    def start(self, exc=ValueError):
        """Populate the game board."""
        log.info("starting the game...")
        if self.started:
            raise exc("The game has already started.")
        elif len(self.players) < 2:
            raise exc("At least 2 players are required.")
        else:
            self.board = Board.randomize(self.players)
            self.turn = 1

    def advance(self, exc=ValueError):
        """Start the next turn."""
        log.info("starting the next turn...")
        if not self.started:
            raise exc("The game has not started.")

        # End every players turn
        for player in self.players:
            player.turn.done = True

        # TODO: update the board

        # Start the next turn
        self.turn += 1
        for player in self.players:
            player.turn.done = False

"""Classes representing games."""

import string
import random

from .. import common
from .player import Players
from .turn import Turn

log = common.logger(__name__)


class Game:

    """An individual game instance."""

    KEY_CHARS = string.ascii_lowercase + string.digits
    KEY_LENGTH = 8

    def __init__(self, key=None):
        self.key = key or self._generate_key()
        self.players = Players()
        self.turn = 0

    def __repr__(self):
        return "<game: {}>".format(self.key)

    @staticmethod
    def _generate_key():
        return ''.join(random.choice(Game.KEY_CHARS)
                       for _ in range(Game.KEY_LENGTH))

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
        if len(self.players) < 2:
            raise exc("At least 2 players are required.")
        if self.turn == 0:
            self.advance()

    def advance(self):
        log.info("starting the next turn...")
        self.turn += 1
        for player in self.players:
            if player.turns.current:
                player.turns.current.done = True
            player.turns.append(Turn())




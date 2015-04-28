"""Classes representing games."""

import string
import random

from flask import url_for  # TODO: remove this import
import yorm

from .. import common
from .player import Players
from .turn import Turn

log = common.logger(__name__)


@yorm.attr(players=Players)
@yorm.attr(turn=yorm.converters.Integer)
@yorm.sync("data/games/{self.key}.yml")
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

    def serialize(self):
        kwargs = {'_external': True, 'key': self.key}
        game_url = url_for('.games_detail', **kwargs)
        players_url = url_for('.players_list', **kwargs)
        start_url = url_for('.games_start', **kwargs)
        return {'uri': game_url,
                'players': players_url,
                'start': start_url,
                'turn': self.turn}


class Games(dict):

    """A collection of all games in the application."""

    def serialize(self):
        return [url_for('.games_detail',
                        _external=True, key=key) for key in self]

    def create(self):
        game = Game()
        self[game.key] = game
        return game

    def find(self, key, exc=ValueError):
        try:
            player = self[key]
        except KeyError:
            raise exc("The game '{}' does not exist.".format(key)) from None
        else:
            return player

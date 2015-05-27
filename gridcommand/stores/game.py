import os

import yorm

from .. import common
from ..domain import Game

from .base import Store


log = common.logger(__name__)


@yorm.attr(begin=yorm.converters.Integer)
@yorm.attr(end=yorm.converters.Integer)
@yorm.attr(count=yorm.converters.Integer)
class Move(yorm.converters.AttributeDictionary):
    pass


@yorm.attr(all=Move)
class Moves(yorm.converters.SortedList):
    pass


@yorm.attr(moves=Moves)
@yorm.attr(done=yorm.converters.Boolean)
class Turn(yorm.converters.AttributeDictionary):
    pass


@yorm.attr(all=Turn)
class Turns(yorm.converters.List):
    pass


@yorm.attr(color=yorm.converters.String)
@yorm.attr(code=yorm.converters.String)
@yorm.attr(turns=Turns)
class Player(yorm.converters.AttributeDictionary):
    pass


@yorm.attr(all=Player)
class Players(yorm.converters.List):
    pass


@yorm.attr(players=Players)
@yorm.attr(turn=yorm.converters.Integer)
@yorm.sync("data/games/{self.key}.yml")
class GameModel:

    def __init__(self, key):
        self.key = key


class GameStore(Store):

    def create(self, game):
        model = GameModel(key=game.key)
        model.players = game.players
        model.turn = game.turn

    def read(self, key):
        if key:
            path = os.path.join("data", "games", key + ".yml")  # TODO: move this to settings?

            if not os.path.exists(path):
                return None

            model = GameModel(key)

            game = Game(key=model.key)
            game.players = model.players
            game.turn = model.turn

            return game
        else:
            games = []

            path = os.path.join("data", "games")  # TODO: move this to settings?
            if os.path.exists(path):
                for filename in os.listdir(path):
                    key = filename.split('.')[0]

                    model = GameModel(key)

                    game = Game(key=model.key)
                    game.players = model.players
                    game.turn = model.turn

                    games.append(game)

            return games

    def update(self, game):
        path = os.path.join("data", "games", game.key + ".yml")  # TODO: move this to settings?
        assert os.path.exists(path)

        model = GameModel(game.key)
        model.players = game.players
        model.turn = game.turn

    def delete(self, game):
        path = os.path.join("data", "games", game.key + ".yml")  # TODO: move this to settings?
        if os.path.exists(path):
            os.remove(path)


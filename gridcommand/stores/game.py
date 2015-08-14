import os

import yorm

from .. import common
from .. import domain
from .base import Store


log = common.logger(__name__)


@yorm.attr(begin=yorm.converters.Integer)
@yorm.attr(end=yorm.converters.Integer)
@yorm.attr(count=yorm.converters.Integer)
class MoveFileModel(yorm.converters.AttributeDictionary, domain.Move):
    pass


@yorm.attr(all=MoveFileModel)
class MovesFileModel(yorm.converters.SortedList, domain.Moves):
    pass


@yorm.attr(moves=MovesFileModel)
@yorm.attr(done=yorm.converters.Boolean)
class TurnFileModel(yorm.converters.AttributeDictionary, domain.Turn):

    def __init__(self):
        super().__init__()
        self.moves = []
        self.done = False


@yorm.attr(color=yorm.converters.String)
@yorm.attr(code=yorm.converters.String)
@yorm.attr(turn=TurnFileModel)
class PlayerFileModel(yorm.converters.AttributeDictionary, domain.Player):

    def __init__(self, color, code, turn=None):
        super().__init__()
        self.color = color
        self.code = code
        self.turn = turn or TurnFileModel()


@yorm.attr(all=PlayerFileModel)
class PlayersFileModel(yorm.converters.List, domain.Players):
    pass


class BoardFileModel(yorm.converters.AttributeDictionary, domain.Board):
    pass


@yorm.attr(timestamp=yorm.converters.Integer)
@yorm.attr(players=PlayersFileModel)
@yorm.attr(turn=yorm.converters.Integer)
@yorm.attr(board=BoardFileModel)
@yorm.sync("data/games/{self.key}.yml", auto=False)
class GameFileModel(domain.Game):

    def __init__(self, key, timestamp=0, turn=0, players=None, board=None):
        super().__init__()
        self.key = key
        self.timestamp = timestamp
        self.turn = turn
        self.players = players or PlayersFileModel()
        self.board = board or BoardFileModel()


class GameMemoryStore(Store):

    def __init__(self):
        self._games = {}

    def create(self, game):
        self._games[game.key] = game
        return game

    def read(self, key):
        assert key
        try:
            return self._games[key]
        except KeyError:
            return None

    def filter(self):
        return list(self._games.values())

    def update(self, game):
        self._games[game.key] = game

    def delete(self, game):
        try:
            del self._games[game.key]
        except KeyError:
            pass


class GameFileStore(Store):

    def create(self, game):
        game = GameFileModel(key=game.key,
                             timestamp=game.timestamp,
                             players=game.players,
                             turn=game.turn,
                             board=game.board)
        yorm.update_file(game)
        return game

    def read(self, key):
        assert key
        path = os.path.join("data", "games", key + ".yml")  # TODO: move this to settings?

        if not os.path.exists(path):
            return None

        game = GameFileModel(key)
        yorm.update_object(game)

        return game

    def filter(self):
        games = []

        path = os.path.join("data", "games")  # TODO: move this to settings?
        if os.path.exists(path):
            for filename in os.listdir(path):
                key = filename.split('.')[0]

                game = GameFileModel(key)
                yorm.update_object(game)

                games.append(game)

        return games

    def update(self, game):
        path = os.path.join("data", "games", game.key + ".yml")  # TODO: move this to settings?
        assert os.path.exists(path)

        yorm.update_file(game)

    def delete(self, game):
        path = os.path.join("data", "games", game.key + ".yml")  # TODO: move this to settings?
        if os.path.exists(path):
            os.remove(path)

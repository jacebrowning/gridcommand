import os
import logging

import yorm

from .. import domain
from ..extensions import mongo
from ._bases import Store


log = logging.getLogger(__name__)


@yorm.attr(begin=yorm.types.Integer)
@yorm.attr(end=yorm.types.Integer)
@yorm.attr(count=yorm.types.Integer)
class MoveFileModel(yorm.types.AttributeDictionary, domain.Move):
    pass


@yorm.attr(all=MoveFileModel)
class MovesFileModel(yorm.types.SortedList, domain.Moves):
    pass


@yorm.attr(moves=MovesFileModel)
@yorm.attr(done=yorm.types.Boolean)
class TurnFileModel(yorm.types.AttributeDictionary, domain.Turn):

    def __init__(self, moves=None, done=None):
        super().__init__()
        self.moves = moves or []
        self.done = done or False


@yorm.attr(color=yorm.types.String)
@yorm.attr(code=yorm.types.String)
@yorm.attr(turn=TurnFileModel)
class PlayerFileModel(yorm.types.AttributeDictionary, domain.Player):

    def __init__(self, color, code, turn=None):
        super().__init__()
        self.color = color
        self.code = code
        self.turn = turn or TurnFileModel()


@yorm.attr(all=PlayerFileModel)
class PlayersFileModel(yorm.types.List, domain.Players):
    pass


class BoardFileModel(yorm.types.AttributeDictionary, domain.Board):
    pass


@yorm.attr(timestamp=yorm.types.Integer)
@yorm.attr(players=PlayersFileModel)
@yorm.attr(turn=yorm.types.Integer)
@yorm.attr(board=BoardFileModel)
@yorm.sync("data/games/{self.key}.yml", auto_create=False, auto_save=False)
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
        return yorm.create(GameFileModel, game.key, game.timestamp, game.turn,
                           game.players, game.board, overwrite=True)

    def read(self, key):
        return yorm.find(GameFileModel, key)

    def filter(self):
        games = []

        path = os.path.join("data", "games")  # TODO: move this to settings?
        if os.path.exists(path):
            for filename in os.listdir(path):
                key = filename.split('.')[0]

                game = GameFileModel(key)
                games.append(game)

        return games

    def update(self, game):
        yorm.save(game)

    def delete(self, game):
        model = yorm.find(GameFileModel, game.key)
        if model:
            yorm.delete(model)


class GameMongoStore(GameFileStore):

    def create(self, game):
        model = super().create(game)

        data = model.__mapper__.data
        data['_id'] = game.key

        log.debug("Creating document: %s", data)
        result = mongo.db.games.insert_one(data)
        log.debug(result)

        return model

    def read(self, key):
        data = mongo.db.games.find_one(key)
        log.debug("Read document: %s", data)

        if not data:
            return None

        key = data.pop('_id')
        model = GameFileModel(key)
        model.__mapper__.create()
        model.__mapper__.data = data

        return model

    def filter(self):
        models = []

        for data in mongo.db.games.find():
            log.debug("Read document: %s", data)
            key = data.pop('_id')
            model = GameFileModel(key)
            model.__mapper__.create()
            model.__mapper__.data = data
            models.append(model)

        return models

    def update(self, game):
        super().update(game)

        model = super().read(game.key)

        data = model.__mapper__.data
        data['_id'] = game.key

        log.debug("Updating document: %s", data)
        result = mongo.db.games.replace_one({'_id': data['_id']}, data)
        log.debug(result)

    def delete(self, game):
        mongo.db.games.delete_one({'_id': game.key})
        super().delete(game)

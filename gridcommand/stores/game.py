import os

import yorm

from .. import common
from .. import domain
from .base import Store


log = common.logger(__name__)


@yorm.attr(begin=yorm.converters.Integer)
@yorm.attr(end=yorm.converters.Integer)
@yorm.attr(count=yorm.converters.Integer)
class MoveFileModel(yorm.converters.AttributeDictionary):
    pass


@yorm.attr(all=MoveFileModel)
class MovesFileModel(yorm.converters.SortedList):
    pass


@yorm.attr(moves=MovesFileModel)
@yorm.attr(done=yorm.converters.Boolean)
class TurnFileModel(yorm.converters.AttributeDictionary):
    pass


@yorm.attr(all=TurnFileModel)
class TurnsFileModel(yorm.converters.List):
    pass


@yorm.attr(color=yorm.converters.String)
@yorm.attr(code=yorm.converters.String)
@yorm.attr(turns=TurnsFileModel)
class PlayerFileModel(yorm.converters.AttributeDictionary):
    pass


@yorm.attr(all=PlayerFileModel)
class PlayersFileModel(yorm.converters.List):
    pass


@yorm.attr(players=PlayersFileModel)
@yorm.attr(turn=yorm.converters.Integer)
@yorm.sync("data/games/{self.key}.yml")
class GameFileModel:

    def __init__(self, key):
        self.key = key
        self.players = PlayersFileModel()
        self.turn = 0

    def from_domain(self, game):
        self.players = game.players
        self.turn = game.turn

    def to_domain(self):
        game = domain.Game(key=self.key)

        for player_model in self.players:
            player = domain.Player(color=player_model.color,
                                   code=player_model.code)

            for turn_model in player_model.turns:
                turn = domain.Turn()

                for move_model in turn_model.moves:
                    move = domain.Move(begin=move_model.begin,
                                       end=move_model.end,
                                       count=move_model.count)

                    turn.moves.append(move)

                player.turns.append(turn)

            game.players.append(player)

        game.turn = self.turn

        return game


class GameMemoryStore(Store):

    def __init__(self):
        self._games = {}

    def create(self, game):
        self._games[game.key] = game

    def read(self, key):
        if key:
            try:
                return self._games[key]
            except KeyError:
                return None
        else:
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
        model = GameFileModel(key=game.key)
        model.from_domain(game)

    def read(self, key):
        if key:
            path = os.path.join("data", "games", key + ".yml")  # TODO: move this to settings?

            if not os.path.exists(path):
                return None

            model = GameFileModel(key)
            game = model.to_domain()

            return game
        else:
            games = []

            path = os.path.join("data", "games")  # TODO: move this to settings?
            if os.path.exists(path):
                for filename in os.listdir(path):
                    key = filename.split('.')[0]

                    model = GameFileModel(key)
                    game = model.to_domain()

                    games.append(game)

            return games

    def update(self, game):
        path = os.path.join("data", "games", game.key + ".yml")  # TODO: move this to settings?
        assert os.path.exists(path)

        model = GameFileModel(game.key)
        model.from_domain(game)

    def delete(self, game):
        path = os.path.join("data", "games", game.key + ".yml")  # TODO: move this to settings?
        if os.path.exists(path):
            os.remove(path)

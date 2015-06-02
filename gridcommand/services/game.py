from ..domain import Game

from .base import Service


class GameService(Service):

    def __init__(self, game_store, **kwargs):
        super().__init__(**kwargs)
        self.game_store = game_store

    def create_game(self, key=None):
        game = Game(key=key)
        self.game_store.create(game)
        return game

    def find_game(self, key):
        game = self.game_store.read(key)
        if game is None:
            msg = "The game '{}' does not exist.".format(key)
            raise self.exceptions.missing(msg)
        return game

    def create_player(self, game, code):
        raise NotImplementedError("TODO: implement method")

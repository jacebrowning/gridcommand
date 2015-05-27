from ..domain import Game
from ..stores import GameStore

from .base import Service


class GameService(Service):

    def __init__(self, game_store=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_store = game_store or GameStore()

    def create_game(self):
        game = Game()
        self.game_store.create(game)
        return game

    def find_game(self, key):
        game = self.game_store.read(key)
        if game is None:
            msg = "The game '{}' does not exist.".format(key)
            raise self.exceptions.missing(msg)
        return game

from ..domain import Game

from .base import Service


class GameService(Service):

    def __init__(self, game_store, **kwargs):
        super().__init__(**kwargs)
        self.game_store = game_store

    def create_game(self, key=None, timestamp=None):
        game = Game(key=key, timestamp=timestamp)
        self.game_store.create(game)
        return game

    def find_game(self, key):
        game = self.game_store.read(key)
        if game is None:
            msg = "The game '{}' does not exist.".format(key)
            raise self.exceptions.not_found(msg)
        return game

    def create_player(self, game, code):
        if not code:
            msg = "Player 'code' must be specified."
            raise self.exceptions.missing_input(msg)
        player = game.create_player(code, exc=self.exceptions.permission_denied)
        self.game_store.update(game)
        return player

    def delete_player(self, game, player):
        game.delete_player(player.color, exc=self.exceptions.permission_denied)
        self.game_store.update(game)

    def start_game(self, game):
        game.start(exc=self.exceptions.permission_denied)
        self.game_store.update(game)

    def get_board(self, key):
        game = self.find_game(key)
        if game.board is None:
            msg = "The game has not started."
            raise self.exceptions.not_found(msg)
        else:
            return game.board

    def create_move(self, game, turn, begin, end, count):
        move = turn.moves.set(begin, end, count)
        self.game_store.update(game)
        return move

    def delete_move(self, game, turn, begin, end):
        turn.moves.delete(begin, end)
        self.game_store.update(game)

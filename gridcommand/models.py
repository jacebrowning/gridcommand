import os
import string
import random

from flask import url_for
from flask.ext.api import exceptions  # pylint: disable=E0611,F0401
import yorm


@yorm.attr(begin=yorm.standard.Integer)
@yorm.attr(end=yorm.standard.Integer)
@yorm.attr(count=yorm.standard.Integer)
class Move(yorm.extended.AttributeDictionary):

    def __init__(self, begin, end, count=0):
        super().__init__()
        self.begin = begin
        self.end = end
        self.count = count

    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end

    def __lt__(self, other):
        if self.begin < other.begin:
            return True
        if self.begin > other.begin:
            return False
        return self.end < other.end

    def serialize(self, game, player):
        return {'count': self.count}


@yorm.attr(all=Move)
class Moves(yorm.extended.SortedList):

    def serialize(self, game, player):
        return [url_for('.moves_detail', _external=True,
                        key=game.key, color=player.color,
                        a=move.begin, b=move.end) for move in self]

    def get(self, begin, end):
        move = Move(begin, end)
        for move2 in self:
            if move == move2:
                return move2
        self.append(move)
        return move

    def set(self, begin, end, count):
        move = self.get(begin, end)
        if count is not None:
            move.count = count
        if not move.count:
            self.delete(begin, end)
        return move

    def delete(self, begin, end):
        move = Move(begin, end)
        try:
            self.remove(move)
        except ValueError:
            pass


@yorm.attr(color=yorm.standard.String)
@yorm.attr(moves=Moves)
@yorm.attr(done=yorm.standard.Boolean)
class Player(yorm.extended.AttributeDictionary):

    def __init__(self, color):
        super().__init__()
        self.color = color
        self.moves = Moves()
        self.done = False

    def serialize(self, game):
        moves_url = url_for('.moves_list', _external=True,
                            key=game.key, color=self.color)
        return {'moves': moves_url,
                'done': self.done}


@yorm.attr(all=Player)
class Players(yorm.container.List):

    def serialize(self, game):
        return [url_for('.players_detail', _external=True,
                        key=game.key, color=player.color) for player in self]

    def find(self, color):
        for player in self:
            if player.color == color:
                return player
        raise exceptions.NotFound()


@yorm.attr(players=Players)
@yorm.attr(started=yorm.standard.Boolean)
@yorm.sync("games/{self.key}.yml")
class Game:

    KEY_CHARS = string.ascii_lowercase + string.digits
    KEY_LENGTH = 8

    def __init__(self, key=None):
        self.key = key or self._generate_key()
        self.players = Players()
        self.started = False

    @staticmethod
    def _generate_key():
        return ''.join(random.choice(Game.KEY_CHARS)
                       for _ in range(Game.KEY_LENGTH))

    def serialize(self):
        players_url = url_for('.players_list', _external=True,
                              key=self.key)
        return {'players': players_url,
                'started': self.started}

    def create_player(self):
        player = Player('red')
        self.players.append(player)
        return player


class Games(dict):

    def serialize(self):
        return [url_for('.games_detail',
                        _external=True, key=key) for key in self]

    def find(self, key):
        try:
            player = self[key]
        except KeyError:
            raise exceptions.NotFound() from None
        else:
            return player


games = Games()


def load():
    if os.path.exists("games"):
        for filename in os.listdir("games"):
            _key = filename.split('.')[0]
            games[_key] = Game(_key)

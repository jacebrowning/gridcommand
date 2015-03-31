import os
import string
import random

from flask import request, url_for, redirect
from flask.ext.api import FlaskAPI, status, exceptions
import yorm

app = FlaskAPI(__name__)


@yorm.attr(begin=yorm.standard.Integer)
@yorm.attr(end=yorm.standard.Integer)
@yorm.attr(count=yorm.standard.Integer)
class Move(yorm.extended.AttributeDictionary):

    def __init__(self, begin, end, count=0):
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
        print(self)
        return [url_for('.moves_detail', _external=True,
                key=game.key, color=player.color,
                a=move.begin, b=move.end) for move in self]

    def get(self, begin, end):
        move = Move(begin, end)
        for move2 in self:
            if move == move2:
                return move2
        else:
            self.append(move)
            return move

    def set(self, begin, end, count):
        move = self.get(begin, end)
        move.count = count
        return move

    def delete(self, begin, end):
        move = Move(begin, end)
        try:
            self.remove(move)
        except ValueError:
            pass
        print(self)


@yorm.attr(color=yorm.standard.String)
@yorm.attr(moves=Moves)
@yorm.attr(done=yorm.standard.Boolean)
class Player(yorm.extended.AttributeDictionary):

    def __init__(self, color):
        self.color = color
        self.moves = []
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
if os.path.exists("games"):
    for filename in os.listdir("games"):
        key = filename.split('.')[0]
        games[key] = Game(key)


# routes ###############################################################


@app.route('/')
def index():
    """Display the server version."""
    return {'version': 1,
            'games': url_for('.games_list', _external=True)}


@app.route("/games/", methods=['GET', 'POST'])
def games_list():
    """List or create games."""

    if request.method == 'GET':
        return games.serialize()

    if request.method == 'POST':
        game = Game()
        games[game.key] = game
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.serialize(), status.HTTP_201_CREATED


@app.route("/games/<string:key>/", methods=['GET', 'PUT', 'DELETE'])
def games_detail(key):
    """Retrieve, update or delete games instances."""

    if request.method == 'GET':
        game = games.find(key)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.serialize()

    if request.method == 'PUT':
        game = games.find(key)
        game.started = request.data.get('started', game.started)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.serialize()

    if request.method == 'DELETE':
        games.pop(key, None)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT


@app.route("/games/<string:key>/players/", methods=['GET', 'POST'])
def players_list(key):
    """List or create players."""
    game = games.find(key)

    if request.method == 'GET':
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.players.serialize(game)

    if request.method == 'POST':
        player = game.create_player()
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game), status.HTTP_201_CREATED


@app.route("/games/<string:key>/players/<string:color>/",
           methods=['GET', 'PUT', 'DELETE'])
def players_detail(key, color):
    game = games.find(key)

    if request.method == 'GET':
        player = game.players.find(color)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game)

    if request.method == 'PUT':
        player = game.players.find(color)
        player.done = request.data.get('done', player.done)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game)

    if request.method == 'DELETE':
        game.players.pop(color, None)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT


@app.route("/games/<string:key>/players/<string:color>/moves/",
           methods=['GET', 'POST'])
def moves_list(key, color):
    game = games.find(key)
    player = game.players.find(color)

    if request.method == 'GET':
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.moves.serialize(game, player)

    if request.method == 'POST':
        move = player.moves.set(request.data.get('begin'),
                                request.data.get('end'),
                                request.data.get('count'))
        yorm.update_file(game)  # TODO: remove when unnecessary
        return move.serialize(game, player)


@app.route("/games/<string:key>/players/<string:color>/moves/<int:a>-<int:b>/",
           methods=['GET', 'PUT', 'DELETE'])
def moves_detail(key, color, a, b):
    game = games.find(key)
    player = game.players.find(color)

    if request.method == 'GET':
        move = player.moves.get(a, b)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return move.serialize(game, player)

    if request.method == 'PUT':
        move = player.moves.get(a, b)
        move.count = request.data.get('count', move.count)
        if not move.count:
            player.moves.delete(a, b)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return move.serialize(game, player)

    if request.method == 'DELETE':
        player.moves.delete(a, b)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT


if __name__ == "__main__":
    app.run(debug=True)

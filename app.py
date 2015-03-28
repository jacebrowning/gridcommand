import uuid

from flask import request
from flask.ext.api import FlaskAPI, status, exceptions
import yorm

app = FlaskAPI(__name__)
games = {}


class Move:

    def __init__(self, fro, to, count):
        pass


@yorm.attr(done=yorm.standard.Boolean)
class Player(yorm.container.Dictionary):

    def __init__(self):
        self.done = False


@yorm.attr(all=Player)
class Players(yorm.container.List):
    pass


#@yorm.attr(key=yorm.standard.String)
#@yorm.attr(players=Players)
@yorm.sync("games/{self.key}.yml")
class Game:

    def __init__(self, key=None):
        self.key = key or uuid.uuid4().hex
        self.players = []


def repr_game(game):
    text = game.yorm_mapper._read()
    data = game.yorm_mapper._load(text, game.yorm_path)
    return data


@app.route("/games/", methods=['GET', 'POST'])
def games_list():
    """List or create games."""
    if request.method == 'POST':
        game = Game()
        games[game.key] = game
        return repr_game(game), status.HTTP_201_CREATED

    else:
        assert request.method == 'GET'
        return {key: repr_game(game) for key, game in games.items()}


@app.route("/games/<string:key>/", methods=['GET', 'PUT', 'DELETE'])
def games_detail(key):
    """Retrieve, update or delete games instances."""
    if request.method == 'PUT':
        assert 0

    elif request.method == 'DELETE':
        games.pop(key, None)
        return '', status.HTTP_204_NO_CONTENT

    else:
        assert request.method == 'GET'
        if key not in games:
            raise exceptions.NotFound()
        return repr_game(games[key])


if __name__ == "__main__":
    app.run(debug=True)

from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions  # pylint: disable=E0611,F0401
import yorm

from .models import games


app = FlaskAPI(__name__)


@app.route('/')
def index():
    """Display the server version."""
    return {'version': 1,
            'games': url_for('.games_list', _external=True)}


GAMES_LIST_URL = "/games/"
GAMES_DETAIL_URL = GAMES_LIST_URL + "<string:key>/"


@app.route(GAMES_LIST_URL, methods=['GET', 'POST'])
def games_list():
    """List or create games."""

    if request.method == 'GET':
        return games.serialize()

    if request.method == 'POST':
        game = games.create()
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.serialize(), status.HTTP_201_CREATED


@app.route(GAMES_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def games_detail(key):
    """Retrieve, update or delete games instances."""

    if request.method == 'GET':
        game = games.find(key, exc=exceptions.NotFound)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.serialize()

    if request.method == 'PUT':
        game = games.find(key, exc=exceptions.NotFound)
        game.started = request.data.get('started', game.started)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.serialize()

    if request.method == 'DELETE':
        games.pop(key, None)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT


PLAYERS_LIST_URL = GAMES_DETAIL_URL + "players/"
PLAYERS_DETAIL_URL = PLAYERS_LIST_URL + "<string:color>/"


@app.route(PLAYERS_LIST_URL, methods=['GET', 'POST'])
def players_list(key):
    """List or create players."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.players.serialize(game)

    if request.method == 'POST':
        player = game.players.create(exc=exceptions.PermissionDenied)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game), status.HTTP_201_CREATED


@app.route(PLAYERS_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def players_detail(key, color):
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        player = game.players.find(color, exc=exceptions.NotFound)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game)

    if request.method == 'PUT':
        player = game.players.find(color, exc=exceptions.NotFound)
        player.done = request.data.get('done', player.done)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game)

    if request.method == 'DELETE':
        game.players.delete(color)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT


MOVES_LIST_URL = PLAYERS_DETAIL_URL + "moves/"
MOVES_DETAIL_URL = MOVES_LIST_URL + "<int:begin>-<int:end>/"


@app.route(MOVES_LIST_URL, methods=['GET', 'POST'])
def moves_list(key, color):
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)

    if request.method == 'GET':
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.moves.serialize(game, player)

    if request.method == 'POST':
        move = player.moves.set(request.data.get('begin'),
                                request.data.get('end'),
                                request.data.get('count'))
        yorm.update_file(game)  # TODO: remove when unnecessary
        return move.serialize()


@app.route(MOVES_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def moves_detail(key, color, begin, end):
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)

    if request.method == 'GET':
        move = player.moves.get(begin, end)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return move.serialize()

    if request.method == 'PUT':
        move = player.moves.set(begin, end, request.data.get('count'))
        yorm.update_file(game)  # TODO: remove when unnecessary
        return move.serialize()

    if request.method == 'DELETE':
        player.moves.delete(begin, end)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT

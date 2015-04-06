"""API routes for the game."""

from flask import request, url_for, redirect
from flask.ext.api import FlaskAPI, status, exceptions  # pylint: disable=E0611,F0401
import yorm  # TODO: remove this import

from .data import games

ROOT_URL = "/api/"

GAMES_LIST_URL = ROOT_URL + "games/"
GAMES_DETAIL_URL = GAMES_LIST_URL + "<string:key>/"

PLAYERS_LIST_URL = GAMES_DETAIL_URL + "players/"
PLAYERS_DETAIL_URL = PLAYERS_LIST_URL + "<string:color>/"
PLAYERS_AUTH_URL = PLAYERS_DETAIL_URL + "<string:code>/"


MOVES_LIST_URL = PLAYERS_AUTH_URL + "moves/"
MOVES_DETAIL_URL = MOVES_LIST_URL + "<int:begin>-<int:end>/"

app = FlaskAPI(__name__)  # pylint: disable=C0103


@app.route('/')
def index():
    """Redirect the index to the API."""
    return redirect(url_for('.root'))


@app.route(ROOT_URL)
def root():
    """Get the API version."""
    return {'version': 1,
            'games': url_for('.games_list', _external=True)}


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
    """Retrieve, update or delete a game."""

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


@app.route(PLAYERS_LIST_URL, methods=['GET', 'POST'])
def players_list(key):
    """List or create players for a game."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        yorm.update_file(game)  # TODO: remove when unnecessary
        return game.players.serialize(game)

    if request.method == 'POST':
        code = str(request.data.get('code', ''))
        if not code:
            raise exceptions.ParseError("Player 'code' must be specified.")
        player = game.players.create(code, exc=exceptions.PermissionDenied)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game), status.HTTP_201_CREATED


@app.route(PLAYERS_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def players_detail(key, color):
    """Retrieve, update or delete a game's player."""
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


@app.route(PLAYERS_AUTH_URL, methods=['GET', 'PUT'])
def players_auth(key, color, code):
    """Retrieve a game's player with authentication."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game, auth=True)

    if request.method == 'PUT':
        player.code = request.data.get('code', player.code)
        player.done = request.data.get('done', player.done)
        yorm.update_file(game)  # TODO: remove when unnecessary
        return player.serialize(game, auth=True)


@app.route(MOVES_LIST_URL, methods=['GET', 'POST'])
def moves_list(key, color, code):
    """List or create moves for a player."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

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
def moves_detail(key, color, code, begin, end):
    """Retrieve, update or delete a players's move."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

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
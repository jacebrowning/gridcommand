"""API view for players."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import status, exceptions  # pylint: disable=E0611,F0401

from ..data import games

from . import app
from .game import GAMES_DETAIL_URL


PLAYERS_LIST_URL = GAMES_DETAIL_URL + "/players/"
PLAYERS_DETAIL_URL = PLAYERS_LIST_URL + "<string:color>"
PLAYERS_AUTH_URL = PLAYERS_DETAIL_URL + "-<string:code>"


@app.route(PLAYERS_LIST_URL, methods=['GET', 'POST'])
def players_list(key):
    """List or create players."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        return game.players.serialize(game)

    elif request.method == 'POST':
        code = str(request.data.get('code', ''))
        if not code:
            raise exceptions.ParseError("Player 'code' must be specified.")
        player = game.create_player(code, exc=exceptions.PermissionDenied)
        return player.serialize(game, auth=True), status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@app.route(PLAYERS_DETAIL_URL, methods=['GET'])
def players_detail(key, color):
    """Retrieve a player.."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        player = game.players.find(color, exc=exceptions.NotFound)
        return player.serialize(game)

    else:  # pragma: no cover
        assert None


@app.route(PLAYERS_AUTH_URL, methods=['GET', 'DELETE'])
def players_auth(key, color, code):
    """Retrieve or delete an authenticated player."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        return player.serialize(game, auth=True)

    elif request.method == 'DELETE':
        game.delete_player(color, exc=exceptions.PermissionDenied)
        return '', status.HTTP_204_NO_CONTENT

    else:  # pragma: no cover
        assert None

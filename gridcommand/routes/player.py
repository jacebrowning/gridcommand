"""API view for players."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import status, exceptions  # pylint: disable=E0611,F0401

from . import app
from .game import GAMES_DETAIL_URL
from .formatters import player_formatter as formatter


PLAYERS_LIST_URL = GAMES_DETAIL_URL + "/players/"
PLAYERS_DETAIL_URL = PLAYERS_LIST_URL + "<string:color>"


@app.route(PLAYERS_LIST_URL, methods=['GET', 'POST'])
def players_list(key):
    """List or create players."""
    game = app.service.find_game(key)

    if request.method == 'GET':
        return formatter.format_multiple(game.players, game)

    elif request.method == 'POST':
        code = str(request.data.get('code', ''))
        player = app.service.create_player(game, code)
        return formatter.format_single(player, game, auth=code), \
            status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@app.route(PLAYERS_DETAIL_URL, methods=['GET', 'DELETE'])
def players_detail(key, color):
    """Retrieve a player.

    With authentication (`code` argument), retrieve private details or delete.

    """
    game = app.service.find_game(key)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    if code:
        player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        return formatter.format_single(player, game, auth=code)

    elif request.method == 'DELETE':
        player.authenticate(code, exc=exceptions.AuthenticationFailed)
        app.service.delete_player(game, player)
        return '', status.HTTP_204_NO_CONTENT

    else:  # pragma: no cover
        assert None

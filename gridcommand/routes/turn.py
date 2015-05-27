"""API view for turns."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import exceptions  # pylint: disable=E0611,F0401

from . import app
from .player import PLAYERS_DETAIL_URL


TUNRS_LIST_URL = PLAYERS_DETAIL_URL + "/turns/"
TURNS_DETAIL_URL = TUNRS_LIST_URL + "<int:number>"


@app.route(TUNRS_LIST_URL, methods=['GET'])
def turns_list(key, color):
    """List turns for a player."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        return player.turns.serialize(game, player)

    else:  # pragma: no cover
        assert None


@app.route(TURNS_DETAIL_URL, methods=['GET'])
def turns_detail(key, color, number):
    """Retrieve a players's turn."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        turn = player.turns.find(number, exc=exceptions.NotFound)
        return turn.serialize(game, player, number)

    else:  # pragma: no cover
        assert None

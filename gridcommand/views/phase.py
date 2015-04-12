"""API view for phases."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import exceptions  # pylint: disable=E0611,F0401

from ..data import games

from . import app
from .player import PLAYERS_AUTH_URL


PHASES_LIST_URL = PLAYERS_AUTH_URL + "/phases/"
PHASES_DETAIL_URL = PHASES_LIST_URL + "<int:number>"


@app.route(PHASES_LIST_URL, methods=['GET'])
def phases_list(key, color, code):
    """List phases for a player."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        return player.phases.serialize(game, player)

    else:  # pragma: no cover
        assert None


@app.route(PHASES_DETAIL_URL, methods=['GET'])
def phases_detail(key, color, code, number):
    """Retrieve a players's phase."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        phase = player.phases.find(number, exc=exceptions.NotFound)
        return phase.serialize(game, player, number)

    else:  # pragma: no cover
        assert None

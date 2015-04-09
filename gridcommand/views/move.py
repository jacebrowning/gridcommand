"""API view for moves."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import status, exceptions  # pylint: disable=E0611,F0401
import yorm  # TODO: remove this import

from ..data import games

from . import app
from .phase import PHASES_DETAIL_URL


MOVES_LIST_URL = PHASES_DETAIL_URL + "/moves/"
MOVES_DETAIL_URL = MOVES_LIST_URL + "<int:begin>-<int:end>"


@app.route(MOVES_LIST_URL, methods=['GET', 'POST'])
def moves_list(key, color, code, number):
    """List or create moves for a player."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)
    phase = player.phases.find(number, exc=exceptions.NotFound)

    if request.method == 'GET':
        yorm.update(game)  # TODO: remove when unnecessary
        return phase.moves.serialize(game, player)

    elif request.method == 'POST':
        move = phase.moves.set(request.data.get('begin'),
                               request.data.get('end'),
                               request.data.get('count'))
        yorm.update(game)  # TODO: remove when unnecessary
        return move.serialize()

    else:  # pragma: no cover
        assert None


@app.route(MOVES_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def moves_detail(key, color, code, number, begin, end):
    """Retrieve, update or delete a players's move."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)
    phase = player.phases.find(number, exc=exceptions.NotFound)

    if request.method == 'GET':
        move = phase.moves.get(begin, end)
        yorm.update(game)  # TODO: remove when unnecessary
        return move.serialize()

    elif request.method == 'PUT':
        move = phase.moves.set(begin, end, request.data.get('count'))
        yorm.update(game)  # TODO: remove when unnecessary
        return move.serialize()

    elif request.method == 'DELETE':
        phase.moves.delete(begin, end)
        yorm.update(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT

    else:  # pragma: no cover
        assert None

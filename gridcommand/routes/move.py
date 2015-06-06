"""API view for moves."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import status, exceptions  # pylint: disable=E0611,F0401

from . import app
from .turn import TURNS_DETAIL_URL
from .formatters import move_formatter as formatter


MOVES_LIST_URL = TURNS_DETAIL_URL + "/moves/"
MOVES_DETAIL_URL = MOVES_LIST_URL + "<int:begin>-<int:end>"


@app.route(MOVES_LIST_URL, methods=['GET', 'POST'])
def moves_list(key, color, number):
    """List or create moves for a player."""
    game = app.service.find_game(key)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)
    turn = player.turns.find(number, exc=exceptions.NotFound)

    if request.method == 'GET':
        return formatter.format_multiple(turn.moves, game, player)

    elif request.method == 'POST':
        begin = request.data.get('begin'),
        end = request.data.get('end'),
        count = request.data.get('count')
        move = app.service.create_move(game, turn, begin, end, count)
        return formatter.format_single(move)

    else:  # pragma: no cover
        assert None


@app.route(MOVES_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def moves_detail(key, color, number, begin, end):
    """Retrieve, update or delete a players's move."""
    game = app.service.find_game(key)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)
    turn = player.turns.find(number, exc=exceptions.NotFound)

    if request.method == 'GET':
        move = turn.moves.get(begin, end)
        return formatter.format_single(move)

    elif request.method == 'PUT':
        count = request.data.get('count')
        move = app.service.create_move(game, turn, begin, end, count)
        return formatter.format_single(move)

    elif request.method == 'DELETE':
        app.service.delete_move(game, turn, begin, end)
        return '', status.HTTP_204_NO_CONTENT

    else:  # pragma: no cover
        assert None

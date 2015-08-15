"""API view for turns."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import exceptions  # pylint: disable=E0611,F0401

from ..domain import Turn

from . import app
from .player import PLAYERS_DETAIL_URL
from ._formatters import turn_formatter as formatter


TUNRS_LIST_URL = PLAYERS_DETAIL_URL + "/turns/"
TURNS_DETAIL_URL = TUNRS_LIST_URL + "<int:number>"
TURNS_FINISH_URL = TURNS_DETAIL_URL + "/finish"


@app.route(TUNRS_LIST_URL, methods=['GET'])
def turns_list(key, color):
    """List turns for a player."""
    game = app.service.find_game(key)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        turns = [Turn() for count in range(game.turn)]
        return formatter.format_multiple(turns, game, player)

    else:  # pragma: no cover
        assert None


@app.route(TURNS_DETAIL_URL, methods=['GET'])
def turns_detail(key, color, number):
    """Retrieve a player's turn."""
    game = app.service.find_game(key)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        return formatter.format_single(game, player, number)

    else:  # pragma: no cover
        assert None


@app.route(TURNS_FINISH_URL, methods=['GET', 'POST'])
def turns_finish(key, color, number):
    """Finish a player's turn."""
    game = app.service.find_game(key)
    player = game.players.find(color, exc=exceptions.NotFound)
    code = request.args.get('code')
    player.authenticate(code, exc=exceptions.AuthenticationFailed)
    turn = _get_turn(game, player, number)

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        app.service.finish_turn(game, turn)

    else:  # pragma: no cover
        assert None

    return {'finished': turn.done}


def _get_turn(game, player, number):
    if 1 >= number < game.turn:
        return Turn(done=True)
    elif number == game.turn:
        return player.turn
    else:
        raise exceptions.NotFound

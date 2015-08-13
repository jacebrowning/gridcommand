"""API view for games."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import status, exceptions  # pylint: disable=E0611,F0401

from . import app
from .root import ROOT_URL
from .formatters import game_formatter as formatter
from .formatters import board_formatter


GAMES_LIST_URL = ROOT_URL + "/games/"
GAMES_DETAIL_URL = GAMES_LIST_URL + "<string:key>"
GAMES_START_URL = GAMES_DETAIL_URL + "/start"
GAMES_BOARD_URL = GAMES_DETAIL_URL + "/board"


@app.route(GAMES_LIST_URL, methods=['GET', 'POST'])
def games_list():
    """Create a new game."""

    if request.method == 'GET':
        raise exceptions.PermissionDenied("Games list is hidden.")

    elif request.method == 'POST':
        game = app.service.create_game()
        return formatter.format_single(game), status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@app.route(GAMES_DETAIL_URL, methods=['GET'])
def games_detail(key):
    """Retrieve a game's status."""

    if request.method == 'GET':
        game = app.service.find_game(key)
        return formatter.format_single(game)

    else:  # pragma: no cover
        assert None


@app.route(GAMES_START_URL, methods=['GET', 'POST'])
def games_start(key):
    """Start a game."""
    game = app.service.find_game(key)

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        app.service.start_game(game)

    else:  # pragma: no cover
        assert None

    return {'started': game.started}


@app.route(GAMES_BOARD_URL, methods=['GET'])
@board_formatter.single
def games_board(key):
    """Get the game board."""
    if request.method == 'GET':
        board = app.service.get_board(key)
        return board

    else:  # pragma: no cover
        assert None

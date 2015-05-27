"""API view for games."""
# pylint: disable=R0913

from flask import request
from flask.ext.api import status, exceptions  # pylint: disable=E0611,F0401

from ..services import GameService

from . import app
from .root import ROOT_URL
from .formatters import game_formatter as formatter


GAMES_LIST_URL = ROOT_URL + "/games/"
GAMES_DETAIL_URL = GAMES_LIST_URL + "<string:key>"
GAMES_START_URL = GAMES_DETAIL_URL + "/start"


service = GameService()
service.exceptions.missing = exceptions.NotFound


@app.route(GAMES_LIST_URL, methods=['GET', 'POST'])
def games_list():
    """Create a new game."""

    if request.method == 'GET':
        raise exceptions.PermissionDenied("Games list is hidden.")

    elif request.method == 'POST':
        game = service.create_game()
        return formatter.format_single(game), status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@app.route(GAMES_DETAIL_URL, methods=['GET'])
def games_detail(key):
    """Retrieve a game's status."""

    if request.method == 'GET':
        game = service.find_game(key)
        return formatter.format_single(game)

    else:  # pragma: no cover
        assert None


@app.route(GAMES_START_URL, methods=['GET', 'POST'])
def games_start(key):
    """Start a game."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        game.start(exc=exceptions.PermissionDenied)

    else:  # pragma: no cover
        assert None

    return {'started': game.started}

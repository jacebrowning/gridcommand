"""API view for games."""

from flask import Blueprint, request, current_app as app
from flask_api import status

from ._formatters import game_formatter as formatter, board_formatter


blueprint = Blueprint('games', __name__, url_prefix="/api/games")


@blueprint.route("/", methods=['GET', 'POST'])
def index():
    """Create a new game."""

    if request.method == 'GET':
        games = app.service.find_games()
        return formatter.format_multiple(games)

    elif request.method == 'POST':
        game = app.service.create_game()
        return formatter.format_single(game), status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@blueprint.route("/<string:key>", methods=['GET', 'DELETE'])
def detail(key):
    """Retrieve a game's status."""

    if request.method == 'GET':
        game = app.service.find_game(key)
        return formatter.format_single(game)

    if request.method == 'DELETE':
        app.service.delete_game(key)
        return {}, status.HTTP_204_NO_CONTENT

    else:  # pragma: no cover
        assert None


@blueprint.route("/<string:key>/start", methods=['GET', 'POST'])
def start(key):
    """Start a game."""
    game = app.service.find_game(key)

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        app.service.start_game(game)

    else:  # pragma: no cover
        assert None

    return {'started': game.started}


@blueprint.route("/<string:key>/board", methods=['GET'])
@board_formatter.single
def board(key):
    """Get the game board."""
    if request.method == 'GET':
        return app.service.get_board(key)

    else:  # pragma: no cover
        assert None

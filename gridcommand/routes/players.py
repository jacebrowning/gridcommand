"""API view for players."""

from flask import Blueprint, request, current_app as app
from flask_api import status, exceptions

from .games import blueprint as games
from ._formatters import player_formatter as formatter


blueprint = Blueprint('players', __name__,
                      url_prefix=games.url_prefix + "/<string:key>/players")


@blueprint.route("/", methods=['GET', 'POST'])
def index(key):
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


@blueprint.route("/<string:color>", methods=['GET', 'DELETE'])
def detail(key, color):
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

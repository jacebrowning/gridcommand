"""API view for turns."""

from flask import Blueprint, request, current_app as app
from flask_api import exceptions

from ..domain import Turn

from ._formatters import turn_formatter as formatter


url_prefix = "/api/games/<string:key>/players/<string:color>/turns"
blueprint = Blueprint('turns', __name__, url_prefix=url_prefix)


@blueprint.route("/", methods=['GET'])
def index(key, color):
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


@blueprint.route("/<int:number>", methods=['GET'])
def detail(key, color, number):
    """Retrieve a player's turn."""
    code = request.args.get('code')
    _, player, game = app.service.find_turn(key, color, code, number)

    if request.method == 'GET':
        pass

    else:  # pragma: no cover
        assert None

    return formatter.format_single(game, player, number)


@blueprint.route("/<int:number>/finish", methods=['GET', 'POST'])
def finish(key, color, number):
    """Finish a player's turn."""
    code = request.args.get('code')
    turn, _, game = app.service.find_turn(key, color, code, number)

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        app.service.finish_turn(game, turn)

    else:  # pragma: no cover
        assert None

    return {'finished': turn.done}

"""API view for moves."""

from flask import Blueprint, request, current_app as app
from flask_api import status

from .turns import blueprint as turns
from ._formatters import move_formatter as formatter


blueprint = Blueprint('moves', __name__,
                      url_prefix=turns.url_prefix + "/<int:number>/moves")


@blueprint.route("/", methods=['GET', 'POST'])
def index(key, color, number):
    """List or create moves for a player."""
    code = request.args.get('code')
    turn, player, game = app.service.find_turn(key, color, code, number)

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


@blueprint.route("/<int:begin>-<int:end>", methods=['GET', 'PUT', 'DELETE'])
def detail(key, color, number, begin, end):
    """Retrieve, update or delete a player's move."""
    code = request.args.get('code')
    turn, _, game = app.service.find_turn(key, color, code, number)

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

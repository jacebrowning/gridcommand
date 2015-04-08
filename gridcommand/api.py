"""API routes for the game."""
# pylint: disable=R0913

from flask import request, url_for, redirect
from flask.ext.api import FlaskAPI, status, exceptions  # pylint: disable=E0611,F0401
import yorm  # TODO: remove this import

from .data import games

ROOT_URL = "/api/"

GAMES_LIST_URL = ROOT_URL + "games/"
GAMES_DETAIL_URL = GAMES_LIST_URL + "<string:key>/"
GAMES_START_URL = GAMES_DETAIL_URL + "start"

PLAYERS_LIST_URL = GAMES_DETAIL_URL + "players/"
PLAYERS_DETAIL_URL = PLAYERS_LIST_URL + "<string:color>/"
PLAYERS_AUTH_URL = PLAYERS_DETAIL_URL + "<string:code>/"

PHASES_LIST_URL = PLAYERS_AUTH_URL + "phases/"
PHASES_DETAIL_URL = PHASES_LIST_URL + "<int:number>/"

MOVES_LIST_URL = PHASES_DETAIL_URL + "moves/"
MOVES_DETAIL_URL = MOVES_LIST_URL + "<int:begin>-<int:end>/"

app = FlaskAPI(__name__)  # pylint: disable=C0103


@app.route('/')
def index():
    """Redirect the index to the API."""
    return redirect(url_for('.root'))


@app.route(ROOT_URL)
def root():
    """Get the API version."""
    return {'version': 1,
            'games': url_for('.games_list', _external=True)}


@app.route(GAMES_LIST_URL, methods=['GET', 'POST'])
def games_list():
    """Create a new game."""

    if request.method == 'GET':
        raise exceptions.PermissionDenied("Games list is hidden.")

    elif request.method == 'POST':
        game = games.create()
        yorm.update(game)  # TODO: remove when unnecessary
        return game.serialize(), status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@app.route(GAMES_DETAIL_URL, methods=['GET'])
def games_detail(key):
    """Retrieve a game instance."""

    if request.method == 'GET':
        game = games.find(key, exc=exceptions.NotFound)
        yorm.update(game)  # TODO: remove when unnecessary
        return game.serialize()

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

    yorm.update(game)  # TODO: remove when unnecessary
    return {'started': game.started}


@app.route(PLAYERS_LIST_URL, methods=['GET', 'POST'])
def players_list(key):
    """List or create players for a game."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        yorm.update(game)  # TODO: remove when unnecessary
        return game.players.serialize(game)

    elif request.method == 'POST':
        code = str(request.data.get('code', ''))
        if not code:
            raise exceptions.ParseError("Player 'code' must be specified.")
        player = game.players.create(code, exc=exceptions.PermissionDenied)
        yorm.update(game)  # TODO: remove when unnecessary
        return player.serialize(game, auth=True), status.HTTP_201_CREATED

    else:  # pragma: no cover
        assert None


@app.route(PLAYERS_DETAIL_URL, methods=['GET', 'PUT', 'DELETE'])
def players_detail(key, color):
    """Retrieve, update or delete a game's player."""
    game = games.find(key, exc=exceptions.NotFound)

    if request.method == 'GET':
        player = game.players.find(color, exc=exceptions.NotFound)
        yorm.update(game)  # TODO: remove when unnecessary
        return player.serialize(game)

    elif request.method == 'PUT':
        player = game.players.find(color, exc=exceptions.NotFound)
        player.done = request.data.get('done', player.done)
        yorm.update(game)  # TODO: remove when unnecessary
        return player.serialize(game)

    elif request.method == 'DELETE':
        game.players.delete(color)
        yorm.update(game)  # TODO: remove when unnecessary
        return '', status.HTTP_204_NO_CONTENT

    else:  # pragma: no cover
        assert None


@app.route(PLAYERS_AUTH_URL, methods=['GET', 'PUT'])
def players_auth(key, color, code):
    """Retrieve a game's player with authentication."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        yorm.update(game)  # TODO: remove when unnecessary
        return player.serialize(game, auth=True)

    elif request.method == 'PUT':
        player.code = request.data.get('code', player.code)
        player.done = request.data.get('done', player.done)
        yorm.update(game)  # TODO: remove when unnecessary
        return player.serialize(game, auth=True)

    else:  # pragma: no cover
        assert None


@app.route(PHASES_LIST_URL, methods=['GET'])
def phases_list(key, color, code):
    """List phases for a player."""
    game = games.find(key, exc=exceptions.NotFound)
    player = game.players.find(color, exc=exceptions.NotFound)
    player.authenticate(code, exc=exceptions.AuthenticationFailed)

    if request.method == 'GET':
        yorm.update(game)  # TODO: remove when unnecessary
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
        yorm.update(game)  # TODO: remove when unnecessary
        return phase.serialize(game, player, number)

    else:  # pragma: no cover
        assert None


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

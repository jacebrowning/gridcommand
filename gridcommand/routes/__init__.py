"""API views for the application."""

from flask_api import FlaskAPI, exceptions

from ..services import GameService
from ..stores import GameFileStore

app = FlaskAPI(__name__)  # pylint: disable=C0103
app.service = GameService(game_store=GameFileStore())
app.service.exceptions.not_found = exceptions.NotFound
app.service.exceptions.permission_denied = exceptions.PermissionDenied
app.service.exceptions.missing_input = exceptions.ParseError
app.service.exceptions.authentication_failed = exceptions.AuthenticationFailed

# TODO: replace imports with blueprints
# pylint: disable=wrong-import-position
from . import root, game, player, turn, move  # noqa, loads routes

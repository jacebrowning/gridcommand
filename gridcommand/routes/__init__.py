"""API views for the application."""

from flask_api import FlaskAPI, exceptions

from ..services import GameService
from ..stores import GameFileStore

app = FlaskAPI(__name__)  # pylint: disable=C0103
app.service = GameService(game_store=GameFileStore())
app.service.exceptions.missing = exceptions.NotFound

from . import root, game, player, turn, move  # loads routes

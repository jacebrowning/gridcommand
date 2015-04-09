"""API views for the application."""

from flask.ext.api import FlaskAPI  # pylint: disable=E0611,F0401

app = FlaskAPI(__name__)  # pylint: disable=C0103

from . import root, game, player, phase, move  # loads routes

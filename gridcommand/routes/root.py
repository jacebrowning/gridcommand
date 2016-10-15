"""API entry point."""

from flask import Blueprint, url_for


blueprint = Blueprint('root', __name__)


@blueprint.route("/api")
def index():
    """Get the API version."""
    return {'version': 1,
            'games': url_for('games.index', _external=True)}

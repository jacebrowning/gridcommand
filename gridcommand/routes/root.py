"""API entry point."""

from flask import Blueprint, url_for, redirect


blueprint = Blueprint('root', __name__)


@blueprint.route("/")
def index():
    """Redirect the index to the API."""
    return redirect(url_for('.root'))


@blueprint.route("/api")
def root():
    """Get the API version."""
    return {'version': 1,
            'games': url_for('games.index', _external=True)}

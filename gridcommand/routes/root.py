"""API entry point."""

from flask import url_for, redirect

from . import app


ROOT_URL = "/api"


@app.route('/')
def index():
    """Redirect the index to the API."""
    return redirect(url_for('.root'))


@app.route(ROOT_URL)
def root():
    """Get the API version."""
    return {'version': 1,
            'games': url_for('.games_list', _external=True)}

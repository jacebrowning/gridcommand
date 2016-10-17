"""UI views for the game."""

from flask import Blueprint, Response, render_template


blueprint = Blueprint('web', __name__)


@blueprint.route("/")
def index():
    return Response(render_template("index.html"))


@blueprint.route("/games/<key>")
def board(key):
    return Response(render_template("board.html", key=key))

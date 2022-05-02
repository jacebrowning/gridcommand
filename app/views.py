import datafiles
import log
from flask import Flask, redirect, render_template, request, url_for

from .actions import Move
from .enums import Color, State
from .models import Game

SIZE = 3
UNITS = SIZE * 4
FILL = 2 / 3

LETTERS = "ABCDEFGHJKLMNPQRTUVXYZ"
NUMBERS = "2346789"

app = Flask(__name__)


@app.context_processor
def constants():
    return dict(Color=Color, State=State)


@app.get("/")
def index():
    return redirect(url_for("create"))


@app.get("/game/")
def create():
    game = Game()
    game.initialize()
    return redirect(url_for("setup", code=game.code))


@app.get("/game/<code>/")
def setup(code: str):
    game = Game(code)
    if game.round:
        return redirect(url_for("choose", code=game.code))
    return render_template("game.html", game=game)


@app.get("/game/<code>.json")
def debug(code: str):
    game = Game(code)
    return game.datafile.data


@app.post("/game/<code>/_randomize/")
def randomize(code: str):
    game = Game(code)
    assert game.round == 0
    game.initialize()
    return render_template("board.html", game=game)


@app.get("/game/<code>/player/")
def choose(code: str):
    game = Game(code)
    game.round = game.round or 1
    if "partial" in request.args:
        return render_template("menu/choose.html", game=game)
    return render_template("game.html", game=game)


@app.get("/game/<code>/player/<color>/")
def player(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    with datafiles.frozen(player):
        if game.round > player.round:
            player.round = game.round
            player.state = State.READY
    return render_template("game.html", game=game, player=player)


@app.post("/game/<code>/player/<color>/_plan/")
def player_plan(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    if "partial" in request.args:
        return render_template("menu/plan.html", game=game, player=player)
    player.state = State.PLANNING
    return render_template("board.html", game=game, player=player)


@app.post("/game/<code>/player/<color>/_done/")
def player_done(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    player.state = State.WAITING
    return render_template("board.html", game=game, player=player)


@app.get("/game/<code>/player/<color>/_next")
def player_next(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    player.state = State.READY
    if player.round == game.round:
        with datafiles.frozen(game):
            move: Move
            for move in game.board.fortifications:
                move.perform()
            for move in game.board.border_clashes:
                move.perform()
            # TODO: Handle mass attacks
            # TODO: Handle spoils of war
            for move in game.board.attacks:
                move.perform()
        game.round += 1
    return redirect(url_for("player", code=game.code, color=player.color.key))


@app.post("/game/<code>/_cell/<int:row>/<int:col>/")
def cell(code: str, row: int, col: int):
    game = Game(code)
    cell = game.board[row, col]
    return render_template("cell.html", game=game, cell=cell, editing=True)


@app.post("/game/<code>/_cell/<int:row>/<int:col>/<direction>/")
def move(code: str, row: int, col: int, direction: str):
    game = Game(code)
    cell = game.board[row, col]
    if direction == "center":
        cell.reset()
    else:
        cell.move(1, direction)
    return render_template("cell.html", game=game, cell=cell, editing=True)


if __name__ == "__main__":
    from livereload import Server

    log.reset()
    log.init()
    log.silence("datafiles", allow_warning=True)

    app.debug = True
    server = Server(app.wsgi_app)
    server.watch("*.py")
    server.watch("templates")
    server.watch("data", ignore=lambda _: True)
    server.serve(port=5000)

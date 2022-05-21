import datafiles
import log
from flask import Flask, redirect, render_template, request, url_for

from .enums import Color, State
from .models import Game

app = Flask(__name__)


@app.context_processor
def constants():
    return dict(Color=Color, State=State, debug=app.debug)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/game/")
@app.post("/game/")
def create():
    if request.method == "POST":
        code = request.form["code"].upper()
        game = Game.objects.get_or_none(code)
        if not game:
            log.error(f"No such game: {code}")
            return redirect(url_for("index"))
    else:
        game = Game()
        game.initialize()
    return redirect(url_for("setup", code=game.code))


@app.get("/game/<code>/")
def setup(code: str):
    game = Game(code)
    if game.round:
        return redirect(url_for("choose", code=game.code))
    return render_template("index.html", game=game)


@app.post("/game/<code>/_randomize/")
def randomize(code: str):
    game = Game(code)
    assert game.round == 0
    size = int(request.form.get("size", game.board.size))
    players = int(request.form.get("players", len(game.players)))
    if "shared" in request.form:
        game.shared = request.form["shared"] == "1"
    else:
        game.initialize(size, players)
    return render_template("board.html", game=game)


@app.get("/game/<code>/player/")
def choose(code: str):
    game = Game(code)
    game.round = game.round or 1
    if "partial" in request.args:
        return render_template("board.html", game=game)
    return render_template("index.html", game=game)


@app.get("/game/<code>/player/<color>/")
def player(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    with datafiles.frozen(player):
        if game.round > player.round:
            player.round = game.round
            player.state = State.READY
        if player.autoplay:
            player.state = State.WAITING
    if "partial" in request.args:
        return render_template("board.html", game=game, player=player)
    return render_template("index.html", game=game, player=player)


@app.post("/game/<code>/player/<color>/_plan/")
def player_plan(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    if "partial" not in request.args:
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
            game.advance()
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
    with datafiles.frozen(cell):
        if direction == "center":
            cell.center = cell.center + cell.up + cell.down + cell.left + cell.right
            cell.up = cell.down = cell.left = cell.right = 0
        elif cell.center:
            cell.center -= 1
            value = getattr(cell, direction)
            setattr(cell, direction, value + 1)
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

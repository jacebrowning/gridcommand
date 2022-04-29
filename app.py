import random
from enum import Enum
from functools import cached_property
from typing import Iterator

import datafiles
from datafiles import datafile, field
from flask import Flask, redirect, render_template, request, url_for

SIZE = 3
UNITS = SIZE * 4
FILL = 2 / 3

CODES = "ABCDEFGHJKLMNPQRSTUVXYZ23456789"

app = Flask(__name__)


class Color(Enum):
    BLUE = "primary"
    RED = "danger"
    GREEN = "success"
    YELLOW = "warning"

    NONE = "dark"

    @property
    def key(self) -> str:
        return self.name.lower()

    @property
    def title(self) -> str:
        return self.name.title()


class State(Enum):
    UNKNOWN = None
    READY = "ready"
    PLANNING = "planning"
    WAITING = "waiting"

    @property
    def title(self) -> str:
        return self.name.title()


@datafile
class Player:
    color: Color
    round: int = 0
    state: State = State.UNKNOWN


@datafile
class Cell:
    row: int
    col: int

    color: Color = Color.NONE

    center: int = 0
    up: int = 0
    down: int = 0
    left: int = 0
    right: int = 0

    def __bool__(self):
        return self.color is not Color.NONE

    @property
    def value(self) -> int:
        return self.center + self.up + self.down + self.left + self.right

    @property
    def can_move_up(self) -> bool:
        return self.row > 0

    @property
    def can_move_down(self) -> bool:
        return self.row < SIZE - 1

    @property
    def can_move_left(self) -> bool:
        return self.col > 0

    @property
    def can_move_right(self) -> bool:
        return self.col < SIZE - 1

    @property
    def moves(self) -> bool:
        return any((self.up, self.down, self.left, self.right))

    def move(self, count: int, direction: str):
        if self.center:
            with datafiles.frozen(self):
                self.center -= count
                value = getattr(self, direction)
                setattr(self, direction, value + count)

    def reset(self):
        with datafiles.frozen(self):
            self.center = self.center + self.up + self.down + self.left + self.right
            self.up = self.down = self.left = self.right = 0


@datafile
class Board:

    cells: list[Cell] = field(default_factory=list)

    def __iter__(self) -> Iterator[list[Cell]]:
        index = 0
        row = []
        for cell in self.cells:
            if cell.row == index:
                row.append(cell)
            else:
                yield row
                row = [cell]
                index += 1
        yield row

    def __getitem__(self, xy) -> Cell:
        row, col = xy
        for cell in self.cells:
            if cell.row == row and cell.col == col:
                return cell
        raise LookupError(f"Unknown cell: {xy}")

    def reset(self):
        assert SIZE <= 5  # see board.html width limits
        self.cells = []
        for row in range(SIZE):
            for col in range(SIZE):
                self.cells.append(Cell(row, col))


@datafile("data/games/{self.code}.yml", defaults=True)
class Game:

    code: str = field(
        default_factory=lambda: "".join(random.choices(CODES, k=4)).lower()
    )

    round: int = 0
    players: list[Player] = field(
        # TODO: Support more than two players
        default_factory=lambda: [Player(Color.BLUE), Player(Color.RED)]
    )
    board: Board = Board()

    @cached_property
    def url(self) -> str:
        return url_for("setup", code=self.code, _external=True)

    @cached_property
    def choosing(self) -> int:
        return sum(1 for p in self.players if p.state is State.UNKNOWN)

    @cached_property
    def waiting(self) -> int:
        if any(p.round < self.round for p in self.players):
            return 0
        return sum(1 for p in self.players if p.state is not State.WAITING)

    @property
    def message(self) -> str:
        if self.round == 0:
            return ""
        if self.choosing:
            s = "" if self.choosing == 1 else "s"
            return f"Waiting for {self.choosing} player{s} to pick a color..."
        if self.waiting:
            s = "" if self.waiting == 1 else "s"
            return f"Waiting for {self.waiting} player{s} to plan moves..."
        return ""

    def initialize(self):
        units = {player.color: UNITS for player in self.players}
        cells = {player.color: [] for player in self.players}
        with datafiles.frozen(self):
            self.board.reset()
            for cell in self.board.cells:
                if random.random() < FILL:
                    player = random.choice(self.players)
                    cell.color = player.color
                    cell.center = 1
                    units[player.color] -= 1
                    cells[player.color].append(cell)
            for color, count in units.items():
                for _ in range(count):
                    cell = random.choice(cells[color])
                    cell.center += 1

    def get_player(self, color: str) -> Player:
        _color = Color[color.upper()]
        for player in self.players:
            if player.color is _color:
                return player
        raise ValueError(f"Unknown player color: {color}")


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


@app.post("/game/<code>/_randomize/")
def randomize(code: str):
    game = Game(code)
    assert game.round == 0
    game.initialize()
    return render_template("board.html", game=game)


@app.get("/game/<code>/player/")
def choose(code: str):
    game = Game(code)
    game.round = 1
    if "partial" in request.args:
        return render_template("players.html", game=game)
    return render_template("game.html", game=game)


@app.get("/game/<code>/player/<color>/")
def player(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
    with datafiles.frozen(player):
        player.round = game.round
        if player.state is State.UNKNOWN:
            player.state = State.READY
    return render_template("game.html", game=game, player=player)


@app.post("/game/<code>/player/<color>/_plan/")
def player_plan(code: str, color: str):
    game = Game(code)
    player = game.get_player(color)
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
            for cell in game.board.cells:
                # TODO: Actually process moves
                cell.up = cell.down = cell.left = cell.right = 0
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

    app.debug = True
    server = Server(app.wsgi_app)
    server.watch("*.py")
    server.watch("templates")
    server.watch("data", ignore=lambda _: True)
    server.serve(port=5000)
